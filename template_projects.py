"""Utilities for initializing template projects from skeletons."""

import shutil
import tempfile
from pathlib import Path


def create_project_instance(project_name: str, target_dir: str = None) -> Path:
    """
    Create a fresh instance of a template project.
    
    Copies the template project from projects/<name>/ to a temporary directory
    and returns the path for the agent to work in.
    
    Args:
        project_name: Name of the project (e.g., "pid_controller", "uart_driver")
        target_dir: Optional target directory. If None, creates temp directory.
    
    Returns:
        Path to the created project instance
    
    Example:
        >>> project_path = create_project_instance("pid_controller")
        >>> print(project_path)
        /tmp/tmp12345/pid_controller
        >>> (project_path / "src/pid.c").exists()
        True
    """
    # Find the template project
    workspace_root = Path(__file__).parent
    template_project = workspace_root / "projects" / project_name
    
    if not template_project.exists():
        raise FileNotFoundError(f"Template project not found: {template_project}")
    
    # Create target directory
    if target_dir is None:
        target_dir = Path(tempfile.mkdtemp())
    else:
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy project to target
    instance_path = target_dir / project_name
    if instance_path.exists():
        shutil.rmtree(instance_path)
    
    shutil.copytree(
        template_project,
        instance_path,
        ignore=shutil.ignore_patterns("build", "__pycache__", "*.pyc")
    )
    
    return instance_path


def get_template_projects() -> list:
    """Get list of available template projects."""
    workspace_root = Path(__file__).parent
    projects_dir = workspace_root / "projects"
    
    projects = []
    for project_dir in projects_dir.iterdir():
        if project_dir.is_dir() and (project_dir / "CMakeLists.txt").exists():
            projects.append(project_dir.name)
    
    return sorted(projects)


def reset_project(project_path: str) -> None:
    """
    Reset a project to skeleton state (remove build artifacts, clear implementations).
    
    Args:
        project_path: Path to the project directory
    """
    project_path = Path(project_path)
    
    # Remove build directory
    build_dir = project_path / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Reset implementation files to stubs
    src_files = {
        "pid_controller": ["src/pid.c"],
        "uart_driver": ["src/uart_frame.c"],
    }
    
    project_name = project_path.name
    if project_name in src_files:
        for src_file in src_files[project_name]:
            filepath = project_path / src_file
            if filepath.exists():
                # Get the minimal stub
                if "pid.c" in str(filepath):
                    filepath.write_text('#include "pid.h"\n\n/* TODO: implement */\n')
                elif "uart_frame.c" in str(filepath):
                    filepath.write_text('#include "uart_frame.h"\n\n/* TODO: implement */\n')


if __name__ == "__main__":
    # Demo: list available projects and create an instance
    print("Available template projects:")
    for proj in get_template_projects():
        print(f"  - {proj}")
    
    print("\nCreating instance of pid_controller...")
    instance = create_project_instance("pid_controller")
    print(f"Instance created at: {instance}")
    print(f"Files:")
    for f in sorted(instance.rglob("*")):
        if f.is_file():
            relpath = f.relative_to(instance)
            print(f"  {relpath}")
