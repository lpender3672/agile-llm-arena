from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass


DEFINITION = {
    "name": "run_mutation",
    "description": (
        "Run mutation testing with MULL for C/C++ projects. "
        "Returns the mutation score (fraction of mutants killed) and details of surviving mutants. "
        "Use this feedback to identify which code paths your tests do not exercise, "
        "then add targeted tests to kill those mutants. Requires CMake-based project with mull.yml."
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


def _ensure_built(cwd: str) -> bool:
    """Ensure the project is built with CMake. Returns True if build successful."""
    build_dir = os.path.join(cwd, "build")
    
    # Create build directory if needed
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    # Configure with CMake
    config_proc = subprocess.run(
        ["cmake", "..", "-DCMAKE_C_COMPILER=clang", "-DCMAKE_CXX_COMPILER=clang++"],
        cwd=build_dir, capture_output=True, text=True, timeout=30,
    )
    if config_proc.returncode != 0:
        return False
    
    # Build with CMake
    build_proc = subprocess.run(
        ["cmake", "--build", "."],
        cwd=build_dir, capture_output=True, text=True, timeout=60,
    )
    return build_proc.returncode == 0


def run(cwd: str) -> MutationResult:
    """Run MULL mutation testing and return a structured MutationResult."""
    # First ensure the project is built
    if not _ensure_built(cwd):
        return MutationResult(
            score=0.0, killed=0, survived=0, total=0,
            error="CMake build failed for mutation testing"
        )
    
    # Run MULL
    mull_proc = subprocess.run(
        ["mull-runner", "-config", "mull.yml", "--log-level=info"],
        cwd=cwd, capture_output=True, text=True, timeout=600,
    )
    
    combined = mull_proc.stdout + mull_proc.stderr
    killed = survived = 0
    
    # Parse MULL output for mutation statistics
    if m := re.search(r"Killed:\s*(\d+)", combined):
        killed = int(m.group(1))
    if m := re.search(r"Survived:\s*(\d+)", combined):
        survived = int(m.group(1))
    
    total = killed + survived
    score = killed / total if total else 0.0
    
    # MULL exits non-zero when mutants survive, that's not an error
    error = None
    if mull_proc.returncode not in (0, 1):
        error = mull_proc.stderr[:500] if mull_proc.stderr else "MULL runner failed"
    
    return MutationResult(score=score, killed=killed, survived=survived, total=total, error=error)


def _surviving_mutants_info(cwd: str) -> str:
    """Get information about surviving mutants from MULL output."""
    # MULL creates html/json reports we can parse
    mull_proc = subprocess.run(
        ["mull-runner", "-config", "mull.yml", "-report-dir", "mull-report"],
        cwd=cwd, capture_output=True, text=True, timeout=600,
    )
    
    output = mull_proc.stdout[:6000]
    return output if output else "(see mull-report/ directory for detailed mutation report)"


def execute(inputs: dict, cwd: str) -> str:
    """Skill execution entry point — returns JSON string for the model."""
    result = run(cwd)
    
    if result.error:
        mutant_info = f"Error: {result.error}"
    elif result.survived > 0:
        mutant_info = _surviving_mutants_info(cwd)
    else:
        mutant_info = "(none — all mutants killed!)"
    
    return json.dumps({
        "mutation_score": round(result.score, 4),
        "killed": result.killed,
        "survived": result.survived,
        "total": result.total,
        "error": result.error,
        "surviving_mutant_info": mutant_info,
    })
