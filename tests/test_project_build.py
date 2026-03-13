"""Test that gtest projects compile and run successfully with CMake and LLVM Clang."""

import os
import subprocess
import shutil
import sys
from pathlib import Path


def get_workspace_root():
    """Get the workspace root directory."""
    return Path(__file__).parent.parent


def get_project_path(project_name):
    """Get the path to a project."""
    return get_workspace_root() / "projects" / project_name


def get_exe_suffix():
    """Get the executable suffix for the current platform."""
    return ".exe" if sys.platform == "win32" else ""


def clean_build_dir(project_path):
    """Clean build directory if it exists."""
    build_dir = project_path / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)


def configure_project(project_path, compiler="clang"):
    """Configure a project with CMake using specified compiler.
    
    Returns:
        True if successful, False otherwise
    """
    build_dir = project_path / "build"
    build_dir.mkdir(exist_ok=True)
    
    result = subprocess.run(
        ["cmake", "..", f"-DCMAKE_C_COMPILER={compiler}"],
        cwd=str(build_dir),
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.returncode == 0


def build_project(project_path):
    """Build a project with CMake.
    
    Returns:
        True if successful, False otherwise
    """
    build_dir = project_path / "build"
    
    result = subprocess.run(
        ["cmake", "--build", ".", "--config", "Debug"],
        cwd=str(build_dir),
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.returncode == 0


def run_gtest(test_exe_path):
    """Run a gtest executable.
    
    Returns:
        True if all tests passed, False otherwise
    """
    result = subprocess.run(
        [str(test_exe_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0


def test_pid_controller_compiles():
    """Test that PID controller project compiles with CMake and Clang."""
    project_path = get_project_path("pid_controller")
    clean_build_dir(project_path)
    
    # Configure
    assert configure_project(project_path), "CMake configuration failed"
    
    # Build
    assert build_project(project_path), "CMake build failed"
    
    # Check that test executable was created
    exe_suffix = get_exe_suffix()
    test_exe = project_path / "build" / f"test_pid{exe_suffix}"
    assert test_exe.exists(), f"Test executable not found: {test_exe}"


def test_uart_driver_compiles():
    """Test that UART driver project compiles with CMake and Clang."""
    project_path = get_project_path("uart_driver")
    clean_build_dir(project_path)
    
    # Configure
    assert configure_project(project_path), "CMake configuration failed"
    
    # Build
    assert build_project(project_path), "CMake build failed"
    
    # Check that test executable was created
    exe_suffix = get_exe_suffix()
    test_exe = project_path / "build" / f"test_uart_frame{exe_suffix}"
    assert test_exe.exists(), f"Test executable not found: {test_exe}"


def test_pid_controller_runs():
    """Test that PID controller gtest executable runs."""
    project_path = get_project_path("pid_controller")
    clean_build_dir(project_path)
    
    # Configure and build
    assert configure_project(project_path), "CMake configuration failed"
    assert build_project(project_path), "CMake build failed"
    
    # Run test
    exe_suffix = get_exe_suffix()
    test_exe = project_path / "build" / f"test_pid{exe_suffix}"
    assert test_exe.exists(), f"Test executable not found: {test_exe}"
    assert run_gtest(test_exe), "GTest execution failed"


def test_uart_driver_runs():
    """Test that UART driver gtest executable runs."""
    project_path = get_project_path("uart_driver")
    clean_build_dir(project_path)
    
    # Configure and build
    assert configure_project(project_path), "CMake configuration failed"
    assert build_project(project_path), "CMake build failed"
    
    # Run test
    exe_suffix = get_exe_suffix()
    test_exe = project_path / "build" / f"test_uart_frame{exe_suffix}"
    assert test_exe.exists(), f"Test executable not found: {test_exe}"
    assert run_gtest(test_exe), "GTest execution failed"

