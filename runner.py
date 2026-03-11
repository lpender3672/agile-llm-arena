"""
Benchmark runner — orchestrates model × workflow × project combinations.
Writes results to results/<timestamp>.json for later analysis.
"""

import asyncio
import json
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

import yaml

from providers import make_provider
from skills.run_mutation import MutationResult, run as run_mutation
from workflows import WORKFLOWS


UNITY_URL = "https://github.com/ThrowTheSwitch/Unity/raw/master/src"
UNITY_FILES = ["unity.c", "unity.h", "unity_internals.h"]


@dataclass
class BenchmarkRun:
    run_id: str
    model_id: str
    model_display: str
    workflow_id: str
    project_id: str
    # Provider output
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    duration_seconds: float = 0
    turns: int = 0
    provider_error: Optional[str] = None
    # Objective measurements (runner-side, independent of model claims)
    tests_passed: bool = False
    mutation_killed: int = 0
    mutation_survived: int = 0
    mutation_total: int = 0
    mutation_score: float = 0.0
    mutation_error: Optional[str] = None
    # Efficiency metrics
    score_per_1k_tokens: float = 0.0   # primary for API-billed models
    score_per_second: float = 0.0      # primary for self-hosted / Ollama models


async def setup_sandbox(sandbox_base: str, run_id: str, project_skeleton: dict) -> str:
    """Create an isolated sandbox with the project skeleton + Unity test framework."""
    sandbox = os.path.join(sandbox_base, run_id)
    os.makedirs(sandbox, exist_ok=True)

    for rel_path, content in project_skeleton.items():
        full_path = os.path.join(sandbox, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    # Download Unity once and cache it
    unity_cache = os.path.join(sandbox_base, "_unity_cache")
    os.makedirs(unity_cache, exist_ok=True)
    unity_dest = os.path.join(sandbox, "test", "unity")
    os.makedirs(unity_dest, exist_ok=True)

    for fname in UNITY_FILES:
        cached = os.path.join(unity_cache, fname)
        if not os.path.exists(cached):
            result = subprocess.run(
                ["curl", "-sL", f"{UNITY_URL}/{fname}", "-o", cached],
                capture_output=True,
            )
            if result.returncode != 0:
                print(f"  Warning: failed to download Unity/{fname}")
        if os.path.exists(cached):
            shutil.copy(cached, os.path.join(unity_dest, fname))

    return sandbox


def check_tests_pass(sandbox_dir: str) -> bool:
    result = subprocess.run(
        ["make", "test"], cwd=sandbox_dir,
        capture_output=True, timeout=30,
    )
    return result.returncode == 0


async def run_single(
    config: dict,
    model_cfg: dict,
    workflow_id: str,
    project_id: str,
    project_module,
) -> BenchmarkRun:
    run_id = f"{model_cfg['id'].replace('/', '_')}_{workflow_id}_{project_id}_{int(time.time())}"
    print(f"\n[{run_id}] Starting...")

    run = BenchmarkRun(
        run_id=run_id,
        model_id=model_cfg["id"],
        model_display=model_cfg["display"],
        workflow_id=workflow_id,
        project_id=project_id,
    )

    sandbox_base = config["runner"]["sandbox_base"]
    os.makedirs(sandbox_base, exist_ok=True)
    sandbox = await setup_sandbox(sandbox_base, run_id, project_module.SKELETON)

    workflow = WORKFLOWS[workflow_id]
    spec = {**project_module.SPEC, "file_tree": project_module.FILE_TREE}
    prompt = workflow.build_prompt(spec)

    provider = make_provider(model_cfg["provider"], model_cfg["id"])
    try:
        result = await asyncio.wait_for(
            provider.run(
                prompt=prompt,
                system=workflow.system_prompt,
                cwd=sandbox,
                max_tokens=config["runner"]["max_tokens_per_run"],
                allowed_tools=workflow.allowed_tools,
            ),
            timeout=config["runner"]["timeout_seconds"],
        )
        run.input_tokens = result.input_tokens
        run.output_tokens = result.output_tokens
        run.total_tokens = result.total_tokens
        run.duration_seconds = result.duration_seconds
        run.turns = result.turns
        if result.error:
            run.provider_error = result.error
            print(f"  Provider error: {result.error}")
            return run
    except asyncio.TimeoutError:
        run.provider_error = "timeout"
        print("  Timed out")
        return run

    # Objective test check — independent of what the model reported
    try:
        run.tests_passed = check_tests_pass(sandbox)
        print(f"  Tests: {'PASS' if run.tests_passed else 'FAIL'}")
    except subprocess.TimeoutExpired:
        print("  Tests: timed out")
        return run

    if not run.tests_passed:
        return run

    # Objective mutation score — independent of any RunMutation calls the model made
    print("  Running mutation tests...")
    mut: MutationResult = run_mutation(sandbox)
    run.mutation_killed = mut.killed
    run.mutation_survived = mut.survived
    run.mutation_total = mut.total
    run.mutation_score = mut.score
    run.mutation_error = mut.error

    if run.total_tokens > 0:
        run.score_per_1k_tokens = (run.mutation_score * 1000) / run.total_tokens
    if run.duration_seconds > 0:
        run.score_per_second = run.mutation_score / run.duration_seconds

    print(
        f"  Mutation score: {run.mutation_score:.2%} "
        f"({run.mutation_killed}/{run.mutation_total}) | "
        f"score/1k tokens: {run.score_per_1k_tokens:.4f}"
    )
    return run


async def run_benchmark(config_path: str = "config.yaml") -> list[BenchmarkRun]:
    with open(config_path) as f:
        config = yaml.safe_load(f)

    import importlib
    projects = {pid: importlib.import_module(f"projects.{pid}") for pid in config["projects"]}

    combos = [
        (model_cfg, workflow_id, project_id, projects[project_id])
        for model_cfg in config["models"]
        for workflow_id in config["workflows"]
        for project_id in config["projects"]
    ]
    print(f"Running {len(combos)} benchmark combinations...")

    semaphore = asyncio.Semaphore(config["runner"]["parallel_runs"])

    async def bounded_run(args):
        async with semaphore:
            return await run_single(config, *args)

    results = await asyncio.gather(*[bounded_run(c) for c in combos])

    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"results/benchmark_{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print(f"\nResults saved to {out_path}")
    _print_summary(results)
    return results


def _print_summary(results: list[BenchmarkRun]):
    print("\n" + "=" * 70)
    print(f"{'Model':<30} {'Workflow':<14} {'Project':<16} {'Score':>7} {'S/1kT':>8}")
    print("-" * 70)
    for r in sorted(results, key=lambda x: -x.score_per_1k_tokens):
        print(
            f"{r.model_display:<30} {r.workflow_id:<14} {r.project_id:<16} "
            f"{r.mutation_score:>6.1%} {r.score_per_1k_tokens:>8.4f}"
        )


if __name__ == "__main__":
    asyncio.run(run_benchmark())
