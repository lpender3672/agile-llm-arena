# Safety Measures

This document describes the security properties of agile-llm-arena, which executes LLM-generated code in sandboxed environments.

## Threat Model

The system gives language models access to three powerful primitives: **file I/O**, **shell execution**, and **subprocess invocation** (via `make` / `mutmut`). A model can therefore attempt to:

1. Read or write files outside the sandbox
2. Execute arbitrary shell commands (network access, data exfiltration, system modification)
3. Consume unbounded compute, memory, or disk
4. Access API keys or other secrets present in the host environment

## Current Measures

### Timeouts

| Skill | Timeout |
|---|---|
| `Bash` | 30 seconds |
| `RunTests` (`make test`) | 60 seconds |
| `RunMutation` (`mutmut run`) | 300 seconds |
| `RunMutation` (`mutmut results`, `mutmut show`) | 30 seconds each |
| Provider-level (whole run) | Configurable via `config.yaml` `runner.timeout_seconds` |

All subprocess calls use `timeout=` so a model cannot cause an infinite hang.

### Output truncation

- `RunTests` truncates combined stdout+stderr to **8,000 characters** before returning to the model.
- `RunMutation` truncates surviving mutant diffs to **6,000 characters**.
- This prevents a model from being fed unbounded output that could blow up context windows or mask injection.

### Working directory scoping

- All skills receive a `cwd` parameter pointing to the sandbox directory.
- `Read` and `Write` resolve paths via `os.path.join(cwd, inputs["path"])`.
- `Bash`, `RunTests`, and `RunMutation` set `cwd=` on `subprocess.run`.

### Error containment

- `execute_skill()` wraps every skill call in a `try/except Exception`, returning an error string rather than crashing the runner.
- `RunTests` individually catches `FileNotFoundError` and `TimeoutExpired`, always returning valid JSON.

### Isolated sandbox directories

- Each benchmark run gets its own sandbox directory under `sandbox_base/<run_id>/`.
- Sandboxes are not shared between concurrent runs.

### Parallelism control

- `runner.py` uses an `asyncio.Semaphore` gated by `config.yaml` `runner.parallel_runs` to bound concurrent execution.

## Known Gaps

### Path traversal — NOT PREVENTED

`Read` and `Write` do `os.path.join(cwd, inputs["path"])` but **do not validate** that the resolved path stays within the sandbox. A model can supply `../../etc/passwd` or `../../../.env` and it will be read or written.

**Risk:** High. A model can read API keys, overwrite project files, or write to arbitrary locations.

### Bash — unrestricted shell access

The `Bash` skill runs `shell=True` with no command filtering, no restricted PATH, and no blocked commands. A model can:
- `curl` data to an external server
- `rm -rf /` (constrained only by OS permissions)
- Read environment variables (`echo $ANTHROPIC_API_KEY`)
- Install packages, modify the system
- Spawn background processes that outlive the timeout

**Risk:** Critical. This is the single largest attack surface.

### No filesystem isolation

Sandboxes are regular directories on the host filesystem. There are no chroot, mount namespace, or container boundaries. The `cwd` parameter is a convention, not an enforcement mechanism.

### No network isolation

Models can make arbitrary outbound network requests via `Bash` (or via compiled code that `make test` executes).

### No resource limits

Beyond timeouts, there are no limits on:
- Memory consumption
- Disk usage
- Number of processes / threads
- CPU cores

A model could fork-bomb or allocate large amounts of memory within the timeout window.

### Environment variable exposure

API keys (`ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`) are in the environment of the runner process and inherited by all subprocesses. Any `Bash` call can read them.

### No audit logging

Tool calls are not logged to disk. There is no record of what commands a model executed, what files it read/wrote, or what network requests it made.

## Recommended Mitigations

### 1. Path validation (low effort, high impact)

Add sandbox path validation to `Read` and `Write`:
```python
resolved = os.path.realpath(os.path.join(cwd, inputs["path"]))
if not resolved.startswith(os.path.realpath(cwd)):
    return "ERROR: path traversal blocked"
```
This should also be added to any future file-based skills.

### 2. Environment variable scrubbing (low effort, high impact)

Pass a sanitised environment to all subprocess calls that strips API keys:
```python
import os

SENSITIVE_KEYS = {"ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"}

def sandbox_env() -> dict:
    return {k: v for k, v in os.environ.items() if k not in SENSITIVE_KEYS}
```
Then use `env=sandbox_env()` in every `subprocess.run()` call.

### 3. Docker-based sandbox (medium effort, high impact)

Run each benchmark inside a disposable Docker container with:
- No network access (`--network=none`)
- Read-only root filesystem with a writable tmpfs for the sandbox
- Memory and PID limits (`--memory=512m --pids-limit=256`)
- Dropped capabilities (`--cap-drop=ALL`)
- No access to the host environment

This is the single most effective mitigation — it converts all of the "known gaps" above into non-issues.

### 4. Bash command allowlisting (medium effort, medium impact)

If Docker is not feasible, restrict the Bash skill to an allowlist of commands:
```python
ALLOWED_PREFIXES = ["make", "gcc", "cat", "ls", "echo"]
```
Reject anything that doesn't match. This is fragile but reduces the attack surface.

### 5. Audit logging (low effort, medium impact)

Log every `execute_skill()` call with timestamp, skill key, inputs (redacted if sensitive), and output length:
```python
import logging
logger = logging.getLogger("skills.audit")
logger.info(f"skill={skill_key} cwd={cwd} inputs={sanitise(inputs)}")
```
This doesn't prevent attacks but enables post-hoc analysis and detection.

### 6. Resource limits via ulimit / cgroups (low effort, medium impact)

On Linux, wrap subprocess calls with resource limits:
```python
import resource

def preexec_limits():
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))  # 512 MB
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    resource.setrlimit(resource.RLIMIT_FSIZE, (50 * 1024 * 1024, 50 * 1024 * 1024))  # 50 MB

subprocess.run(..., preexec_fn=preexec_limits)
```

### 7. Read-only project skeleton (low effort, low impact)

After writing the project skeleton to the sandbox, mark skeleton files as read-only. This prevents a model from silently modifying the spec or Makefile to make tests trivially pass.

## Priority Order

| Priority | Mitigation | Effort | Impact |
|---|---|---|---|
| 1 | Path validation | Low | Blocks file escape |
| 2 | Environment scrubbing | Low | Blocks secret exfiltration |
| 3 | Audit logging | Low | Enables detection |
| 4 | Docker sandbox | Medium | Comprehensive isolation |
| 5 | Resource limits | Low | Prevents DoS |
| 6 | Bash allowlisting | Medium | Reduces shell attack surface |
| 7 | Read-only skeleton | Low | Prevents spec tampering |
