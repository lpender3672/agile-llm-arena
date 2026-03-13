import json
import os
import subprocess
from pathlib import Path

DEFINITION = {
    "name": "run_tests",
    "description": (
        "Run the project test suite. Supports both CMake-based and Make-based projects. "
        "For CMake projects: automatically configures and builds, then runs tests. "
        "For Make projects: runs 'make test'. "
        "Returns JSON with pass/fail status and full compiler + test output."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}


def _run_cmake_tests(cwd: str) -> tuple[bool, str]:
    """Run tests for a CMake-based project."""
    build_dir = os.path.join(cwd, "build")
    
    # Create build directory if needed
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    # Configure with CMake using Clang
    config_result = subprocess.run(
        ["cmake", "..", "-DCMAKE_C_COMPILER=clang", "-DCMAKE_CXX_COMPILER=clang++"],
        cwd=build_dir, capture_output=True, text=True, timeout=30,
    )
    
    if config_result.returncode != 0:
        return False, f"ERROR (CMake config): {config_result.stderr}"
    
    # Build with CMake
    build_result = subprocess.run(
        ["cmake", "--build", "."],
        cwd=build_dir, capture_output=True, text=True, timeout=120,
    )
    
    if build_result.returncode != 0:
        return False, f"ERROR (CMake build): {build_result.stderr[:2000]}"
    
    # Run tests with CTest
    test_result = subprocess.run(
        ["ctest", "--verbose"],
        cwd=build_dir, capture_output=True, text=True, timeout=300,
    )
    
    output = build_result.stdout + build_result.stderr + test_result.stdout + test_result.stderr
    return test_result.returncode == 0, output[:8000]


def _run_make_tests(cwd: str) -> tuple[bool, str]:
    """Run tests for a traditional Make-based project."""
    result = subprocess.run(
        ["make", "test"], cwd=cwd,
        capture_output=True, text=True, timeout=60,
    )
    return result.returncode == 0, (result.stdout + result.stderr)[:8000]


def execute(inputs: dict, cwd: str) -> str:
    try:
        # Check if CMakeLists.txt exists (CMake project)
        if Path(cwd, "CMakeLists.txt").exists():
            passed, output = _run_cmake_tests(cwd)
        else:
            # Fall back to Make-based build
            passed, output = _run_make_tests(cwd)
        
        return json.dumps({
            "passed": passed,
            "output": output,
        })
    except FileNotFoundError as e:
        # Check which tool is missing
        tool = str(e).split("'")[1] if "'" in str(e) else "build tool"
        return json.dumps({
            "passed": False,
            "output": f"ERROR: '{tool}' not found on PATH. Make sure cmake and clang (or make) are installed.",
        })
    except subprocess.TimeoutExpired:
        return json.dumps({
            "passed": False,
            "output": "ERROR: Test execution timed out (exceeded 300 seconds)",
        })
    except Exception as e:
        return json.dumps({
            "passed": False,
            "output": f"ERROR: {str(e)[:500]}",
        })
