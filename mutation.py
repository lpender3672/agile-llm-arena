"""
Mutation testing integration.
Runs mutmut (or universalmutator) on a completed sandbox and returns a score.
"""

import asyncio
import json
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class MutationResult:
    killed: int
    survived: int
    total: int
    score: float           # killed / total
    timed_out: int = 0
    error: Optional[str] = None


async def run_mutation_score(
    sandbox_dir: str,
    src_file: str,        # relative to sandbox, e.g. "src/ring_buffer.c"
    tool: str = "mutmut",
    timeout: int = 120,
) -> MutationResult:
    if tool == "mutmut":
        return await _run_mutmut(sandbox_dir, src_file, timeout)
    elif tool == "universalmutator":
        return await _run_universalmutator(sandbox_dir, src_file, timeout)
    raise ValueError(f"Unknown mutation tool: {tool}")


async def _run_mutmut(sandbox_dir: str, src_file: str, timeout: int) -> MutationResult:
    # mutmut needs a setup.cfg or pyproject.toml OR can be pointed at a runner
    # For C projects we use the --runner flag to call `make test`
    cmd = [
        "mutmut", "run",
        "--paths-to-mutate", src_file,
        "--runner", "make test",
        "--no-progress",
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=sandbox_dir,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return MutationResult(0, 0, 0, 0.0, error="timeout")

    # Parse results
    result_proc = subprocess.run(
        ["mutmut", "results"], cwd=sandbox_dir,
        capture_output=True, text=True,
    )
    return _parse_mutmut_output(result_proc.stdout)


def _parse_mutmut_output(text: str) -> MutationResult:
    killed = survived = timed_out = 0

    m = re.search(r"(\d+) killed", text)
    if m:
        killed = int(m.group(1))
    m = re.search(r"(\d+) survived", text)
    if m:
        survived = int(m.group(1))
    m = re.search(r"(\d+) timed out", text)
    if m:
        timed_out = int(m.group(1))

    total = killed + survived + timed_out
    score = killed / total if total > 0 else 0.0
    return MutationResult(killed, survived, total, score, timed_out)


async def _run_universalmutator(sandbox_dir: str, src_file: str, timeout: int) -> MutationResult:
    """
    universalmutator workflow:
    1. mutate <src_file> -> produces <src_file>.mutant.* files
    2. For each mutant: swap in, run `make test`, swap back, record pass/fail
    """
    abs_src = os.path.join(sandbox_dir, src_file)

    # Generate mutants
    gen = subprocess.run(
        ["mutate", abs_src, "--mutantDir", os.path.join(sandbox_dir, "mutants")],
        capture_output=True, text=True,
    )
    if gen.returncode != 0:
        return MutationResult(0, 0, 0, 0.0, error=gen.stderr)

    mutant_dir = os.path.join(sandbox_dir, "mutants")
    mutants = sorted(
        f for f in os.listdir(mutant_dir) if f.endswith(".c")
    ) if os.path.isdir(mutant_dir) else []

    with open(abs_src) as f:
        original = f.read()

    killed = survived = 0

    for mutant_file in mutants:
        mutant_path = os.path.join(mutant_dir, mutant_file)
        with open(mutant_path) as f:
            mutant_src = f.read()

        # Swap in mutant
        with open(abs_src, "w") as f:
            f.write(mutant_src)

        # Run test suite
        result = subprocess.run(
            ["make", "test"], cwd=sandbox_dir,
            capture_output=True, timeout=30,
        )
        if result.returncode != 0:
            killed += 1
        else:
            survived += 1

        # Restore original
        with open(abs_src, "w") as f:
            f.write(original)

    total = killed + survived
    score = killed / total if total > 0 else 0.0
    return MutationResult(killed, survived, total, score)
