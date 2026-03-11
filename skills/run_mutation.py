from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass


DEFINITION = {
    "name": "run_mutation",
    "description": (
        "Run mutation testing with mutmut. "
        "Returns the mutation score (fraction of mutants killed) and the unified diffs "
        "of all surviving mutants. Use the diffs to identify which code paths your "
        "tests do not exercise, then add targeted tests to kill those mutants."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}


@dataclass
class MutationResult:
    score: float
    killed: int
    survived: int
    total: int
    error: str | None = None


def run(cwd: str) -> MutationResult:
    """Run mutmut and return a structured MutationResult. Used by runner.py."""
    run_proc = subprocess.run(
        ["mutmut", "run"],
        cwd=cwd, capture_output=True, text=True, timeout=300,
    )
    results_proc = subprocess.run(
        ["mutmut", "results"],
        cwd=cwd, capture_output=True, text=True, timeout=30,
    )
    combined = results_proc.stdout + run_proc.stdout + run_proc.stderr
    killed = survived = 0
    if m := re.search(r"(\d+) killed", combined):
        killed = int(m.group(1))
    if m := re.search(r"(\d+) survived", combined):
        survived = int(m.group(1))
    total = killed + survived
    score = killed / total if total else 0.0
    # mutmut exits 1 when mutants survive — that's not an error
    error = run_proc.stderr[:500] if run_proc.returncode not in (0, 1) else None
    return MutationResult(score=score, killed=killed, survived=survived, total=total, error=error)


def _surviving_diffs(cwd: str) -> str:
    diff_proc = subprocess.run(
        ["mutmut", "show", "all"],
        cwd=cwd, capture_output=True, text=True, timeout=30,
    )
    return diff_proc.stdout[:6000]


def execute(inputs: dict, cwd: str) -> str:
    """Skill execution entry point — returns JSON string for the model."""
    result = run(cwd)
    diffs = _surviving_diffs(cwd) if result.survived > 0 else "(none — all mutants killed!)"
    return json.dumps({
        "mutation_score": round(result.score, 4),
        "killed": result.killed,
        "survived": result.survived,
        "total": result.total,
        "survived_mutant_diffs": diffs,
    })
