# [WIP] agile-llm-arena

Benchmarks LLM × workflow × project combinations for embedded C software quality.
Primary question: which combination of model and workflow achieves the best **mutation score per token** (API models) or **per second** (self-hosted)?

All providers participate via tool-calling APIs. The workflow dimension varies along two axes:
- **Skill set** — which tools the model is granted (`RunTests`, `RunMutation`, etc.)
- **Prompt strategy** — how the task is framed (`tdd`, `impl_first`, `iterative`, `mutation_aware`)

Mutation scores are always measured objectively by the runner after each run, independent of any `RunMutation` calls the model made internally.

## Setup

```bash
pip install -e ".[dev]"
```

API keys (set whichever providers you intend to use):
```bash
export ANTHROPIC_API_KEY=...
export OPENROUTER_API_KEY=...
```

For the Claude Code CLI provider:
```bash
npm install -g @anthropic-ai/claude-code
```

For self-hosted models, start [Ollama](https://ollama.com) with the target model pulled:
```bash
ollama serve
ollama pull qwen2.5-coder:7b
```

## Run

```bash
python runner.py                 # uses config.yaml
python runner.py my_config.yaml  # custom config
```

Results are saved to `results/benchmark_<timestamp>.json`.

## Tests

```bash
pytest
```

## Structure

```
agile-llm-arena/
├── skills/
│   ├── __init__.py        # SKILLS registry, execute_skill, to_openai_tool
│   ├── read.py
│   ├── write.py
│   ├── bash.py
│   ├── run_tests.py       # runs `make test`, returns {passed, output} JSON
│   └── run_mutation.py    # runs mutmut, returns score + surviving diffs JSON
├── providers/
│   ├── __init__.py        # make_provider factory
│   ├── base.py            # Provider ABC, RunResult
│   ├── anthropic.py       # Anthropic Messages API (tool-calling loop)
│   ├── claude_code.py     # Claude Code CLI (autonomous)
│   ├── openai_compat.py   # shared OpenAI-compat tool-calling base
│   ├── openrouter.py      # OpenRouter (Devstral, Gemini Flash, etc.)
│   └── ollama.py          # local Ollama (self-hosted models)
├── workflows/
│   ├── __init__.py        # WORKFLOWS dict
│   ├── base.py            # Workflow dataclass
│   ├── tdd.py
│   ├── impl_first.py
│   ├── iterative.py
│   └── mutation_aware.py  # uses RunTests + RunMutation skills
├── projects/
│   └── <project>/
│       └── __init__.py    # SPEC, SKELETON, FILE_TREE
├── tests/
│   ├── conftest.py
│   ├── test_skills.py
│   ├── test_providers.py
│   └── test_workflows.py
├── runner.py
├── config.yaml
└── pyproject.toml
```

## Adding a Model

In `config.yaml`:
```yaml
models:
  - id: qwen2.5-coder:7b
    provider: ollama
    display: "Qwen2.5-Coder 7B"
```

Providers: `anthropic_api` | `openrouter` | `ollama` | `claude_code_cli`

## Adding a Project

1. Create `projects/<name>/__init__.py` defining `SPEC`, `SKELETON`, `FILE_TREE`
2. Add `<name>` to `config.yaml` under `projects:`

Each project needs:
- A C source skeleton (`src/<module>.c`, `src/<module>.h`)
- A Unity test skeleton (`test/test_<module>.c`)
- A `Makefile` with a `test` target that exits non-zero on failure

## Adding a Workflow

Create `workflows/<name>.py` with a `Workflow(...)` instance, import it into `workflows/__init__.py`, and add the id to `WORKFLOWS`.

## Adding a Skill

Create `skills/<name>.py` with a `DEFINITION` dict (Anthropic tool format) and an `execute(inputs, cwd) -> str` function. Register it in `skills/__init__.py`.

## Metrics

| Metric | Description |
|---|---|
| `mutation_score` | Fraction of mutants killed — primary quality signal |
| `score_per_1k_tokens` | Quality efficiency for API-billed models |
| `score_per_second` | Quality efficiency for self-hosted / Ollama models |
| `tests_passed` | Whether `make test` passed (runner-side check) |
| `total_tokens` | Input + output tokens across all turns |
| `turns` | Number of agentic tool-call rounds |
