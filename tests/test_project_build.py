"""Test that project templates compile and run successfully with CMake and Clang."""

import os
import subprocess
import tempfile
from pathlib import Path


def create_project_from_skeleton(project_path, skeleton_dict):
    """Extract skeleton files to a temporary directory."""
    tempdir = Path(tempfile.mkdtemp())
    for filename, content in skeleton_dict.items():
        filepath = tempdir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
    return tempdir


def test_pid_controller_compiles():
    """Test that PID controller project compiles with CMake and Clang."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from projects.pid_controller import SKELETON
    
    workdir = create_project_from_skeleton("pid_controller", SKELETON)
    
    try:
        # Create build directory
        build_dir = workdir / "build"
        build_dir.mkdir()
        
        # Configure with CMake using Clang
        result = subprocess.run(
            ["cmake", "..", "-DCMAKE_C_COMPILER=clang"],
            cwd=str(build_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"CMake config failed: {result.stderr}"
        
        # Build with CMake
        result = subprocess.run(
            ["cmake", "--build", "."],
            cwd=str(build_dir),
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"CMake build failed: {result.stderr}"
        
        # Check that test executable was created
        test_exe = build_dir / "test_pid"
        assert test_exe.exists(), f"Test executable not found: {test_exe}"
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(workdir)


def test_uart_driver_compiles():
    """Test that UART driver project compiles with CMake and Clang."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from projects.uart_driver import SKELETON
    
    workdir = create_project_from_skeleton("uart_driver", SKELETON)
    
    try:
        # Create build directory
        build_dir = workdir / "build"
        build_dir.mkdir()
        
        # Configure with CMake using Clang
        result = subprocess.run(
            ["cmake", "..", "-DCMAKE_C_COMPILER=clang"],
            cwd=str(build_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"CMake config failed: {result.stderr}"
        
        # Build with CMake
        result = subprocess.run(
            ["cmake", "--build", "."],
            cwd=str(build_dir),
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"CMake build failed: {result.stderr}"
        
        # Check that test executable was created
        test_exe = build_dir / "test_uart_frame"
        assert test_exe.exists(), f"Test executable not found: {test_exe}"
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(workdir)


def test_pid_controller_runs():
    """Test that PID controller test executable runs."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from projects.pid_controller import SKELETON
    
    workdir = create_project_from_skeleton("pid_controller", SKELETON)
    
    try:
        build_dir = workdir / "build"
        build_dir.mkdir()
        
        # Build
        subprocess.run(
            ["cmake", "..", "-DCMAKE_C_COMPILER=clang"],
            cwd=str(build_dir),
            capture_output=True,
            timeout=30,
        )
        subprocess.run(
            ["cmake", "--build", "."],
            cwd=str(build_dir),
            capture_output=True,
            timeout=60,
        )
        
        # Run test
        test_exe = build_dir / "test_pid"
        result = subprocess.run(
            [str(test_exe)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Even empty test should complete successfully
        assert result.returncode == 0, f"Test execution failed: {result.stderr}"
        
    finally:
        import shutil
        shutil.rmtree(workdir)


def test_uart_driver_runs():
    """Test that UART driver test executable runs."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from projects.uart_driver import SKELETON
    
    workdir = create_project_from_skeleton("uart_driver", SKELETON)
    
    try:
        build_dir = workdir / "build"
        build_dir.mkdir()
        
        # Build
        subprocess.run(
            ["cmake", "..", "-DCMAKE_C_COMPILER=clang"],
            cwd=str(build_dir),
            capture_output=True,
            timeout=30,
        )
        subprocess.run(
            ["cmake", "--build", "."],
            cwd=str(build_dir),
            capture_output=True,
            timeout=60,
        )
        
        # Run test
        test_exe = build_dir / "test_uart_frame"
        result = subprocess.run(
            [str(test_exe)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Even empty test should complete successfully
        assert result.returncode == 0, f"Test execution failed: {result.stderr}"
        
    finally:
        import shutil
        shutil.rmtree(workdir)
