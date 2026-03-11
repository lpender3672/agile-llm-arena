# LLM Embedded Software Benchmark

Benchmarks model × workflow × project combinations.
Primary metric: **mutation score increase per token** (`score_per_1k_tokens`).

## Setup

```bash
pip install anthropic openai pyyaml mutmut
npm install -g @anthropic-ai/claude-code  # optional, for claude_code_cli provider

export ANTHROPIC_API_KEY=...
export OPENROUTER_API_KEY=...           # for Devstral, Gemini Flash etc.
```

## Run

```bash
cd llm-benchmark
python -m runner.runner                 # runs all combinations from config.yaml
```

Results saved to `results/benchmark_<timestamp>.json`.

## Structure

```
llm-benchmark/
├── config.yaml                 # models, projects, workflows, runner settings
├── providers/
│   └── adapters.py             # ClaudeCodeCLI | AnthropicAPI | OpenRouter
├── workflows/
│   └── templates.py            # tdd | impl_first | iterative | mutation_aware
├── projects/
│   ├── ring_buffer/            # fixed-size circular buffer
│   ├── pid_controller/         # discrete PID with anti-windup
│   └── uart_driver/            # COBS+CRC8 framing layer
├── runner/
│   ├── runner.py               # orchestrator + sandbox setup
│   └── mutation.py             # mutmut / universalmutator integration
└── dashboard/
    └── Dashboard.jsx           # results visualisation (React)
```

## Adding a Model

In `config.yaml`:
```yaml
models:
  - id: mistral/codestral-latest
    provider: openrouter
    display: "Codestral Latest"
```

Providers: `anthropic_api` | `openrouter` | `claude_code_cli`

## Adding a Project

1. Create `projects/my_project/__init__.py` with `SPEC`, `SKELETON`, `FILE_TREE`
2. Add `my_project` to `config.yaml` under `projects:`

Projects need:
- A C source skeleton (`src/<module>.c`, `src/<module>.h`)
- A Unity test skeleton (`test/test_<module>.c`)  
- A `Makefile` with a `test` target that exits non-zero on failure

## Adding a Workflow

In `workflows/templates.py`, add a `Workflow(...)` instance and register it in `WORKFLOWS`.

## Metrics

| Metric | Description |
|--------|-------------|
| `mutation_score` | Fraction of mutants killed by the test suite |
| `score_per_1k_tokens` | mutation_score × 1000 / total_tokens — the primary efficiency metric |
| `tests_passed` | Whether `make test` passed at all |
| `total_tokens` | Input + output tokens consumed |
| `turns` | Number of agentic turns (1 for non-agentic providers) |

## Notes

- Each run gets an isolated sandbox under `runner.sandbox_base`
- Unity test framework is downloaded once and cached
- OpenRouter provider is single-turn (no agentic loop) — extends well for models that support tool use
- Claude Code CLI provider requires the `claude` binary on PATH
# agile-llm-arena
