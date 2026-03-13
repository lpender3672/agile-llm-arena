"""Project build utilities for CMake-based C/C++ template projects."""

import os
import subprocess
from pathlib import Path
from typing import Optional


class ProjectBuilder:
    """Helper class for building CMake-based projects."""
    
    def __init__(self, project_path: str, build_type: str = "Debug"):
        self.project_path = Path(project_path).resolve()
        self.build_dir = self.project_path / "build"
        self.build_type = build_type
    
    def configure(self, compiler: str = "clang") -> bool:
        """Configure the project with CMake using specified compiler.
        
        Args:
            compiler: C compiler to use (clang, gcc, etc.)
        
        Returns:
            True if configuration successful, False otherwise
        """
        self.build_dir.mkdir(exist_ok=True)
        
        cmd = [
            "cmake",
            "..",
            f"-DCMAKE_BUILD_TYPE={self.build_type}",
            f"-DCMAKE_C_COMPILER={compiler}",
            f"-DCMAKE_CXX_COMPILER={compiler}++" if compiler != "msvc" else "",
        ]
        
        result = subprocess.run(
            [c for c in cmd if c],  # Remove empty strings
            cwd=str(self.build_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        return result.returncode == 0
    
    def build(self) -> bool:
        """Build the project using CMake.
        
        Returns:
            True if build successful, False otherwise
        """
        if not self.build_dir.exists():
            if not self.configure():
                return False
        
        result = subprocess.run(
            ["cmake", "--build", "."],
            cwd=str(self.build_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        return result.returncode == 0
    
    def run_tests(self) -> bool:
        """Run CTest tests in the project.
        
        Returns:
            True if all tests passed, False otherwise
        """
        result = subprocess.run(
            ["ctest", "--verbose"],
            cwd=str(self.build_dir),
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        return result.returncode == 0
    
    def run_mutation_tests(self) -> dict:
        """Run MULL mutation testing.
        
        Returns:
            Dictionary with mutation_score, killed, survived, total
        """
        if not (self.project_path / "mull.yml").exists():
            return {
                "error": "mull.yml not found in project",
                "mutation_score": 0.0,
                "killed": 0,
                "survived": 0,
                "total": 0,
            }
        
        # First build the project
        if not self.build():
            return {
                "error": "Project build failed",
                "mutation_score": 0.0,
                "killed": 0,
                "survived": 0,
                "total": 0,
            }
        
        # Run MULL
        result = subprocess.run(
            ["mull-runner", "-config", "mull.yml", "--log-level=info"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
            timeout=600,
        )
        
        # Parse results
        import re
        output = result.stdout + result.stderr
        
        killed = 0
        survived = 0
        
        if m := re.search(r"Killed:\s*(\d+)", output):
            killed = int(m.group(1))
        if m := re.search(r"Survived:\s*(\d+)", output):
            survived = int(m.group(1))
        
        total = killed + survived
        score = killed / total if total else 0.0
        
        return {
            "mutation_score": score,
            "killed": killed,
            "survived": survived,
            "total": total,
            "error": None,
        }
    
    def clean(self) -> bool:
        """Clean build artifacts.
        
        Returns:
            True if cleanup successful
        """
        if self.build_dir.exists():
            result = subprocess.run(
                ["cmake", "--build", ".", "--target", "clean"],
                cwd=str(self.build_dir),
                capture_output=True,
            )
            if result.returncode == 0:
                import shutil
                shutil.rmtree(self.build_dir)
                return True
        return False


def get_test_executable(project_path: str) -> Optional[Path]:
    """Find the test executable for a project.
    
    Args:
        project_path: Path to the project directory
    
    Returns:
        Path to test executable if found, None otherwise
    """
    build_dir = Path(project_path) / "build"
    if not build_dir.exists():
        return None
    
    # Common test executable names
    test_names = ["test_pid", "test_uart_frame", "test_*"]
    
    for test_name in test_names:
        candidates = list(build_dir.glob(test_name))
        if candidates:
            # Return first executable found
            exe_path = candidates[0]
            if exe_path.is_file():
                return exe_path
    
    return None


def verify_project_compiles(project_path: str) -> bool:
    """Verify that a project compiles successfully.
    
    Args:
        project_path: Path to the project directory
    
    Returns:
        True if project compiles and tests exist, False otherwise
    """
    builder = ProjectBuilder(project_path)
    
    if not builder.configure():
        return False
    
    if not builder.build():
        return False
    
    # Check that test executable was created
    if not get_test_executable(project_path):
        return False
    
    return True


def verify_tests_run(project_path: str) -> bool:
    """Verify that tests compile and run successfully.
    
    Args:
        project_path: Path to the project directory
    
    Returns:
        True if tests run successfully, False otherwise
    """
    builder = ProjectBuilder(project_path)
    
    if not builder.build():
        return False
    
    return builder.run_tests()
