import os
import pytest


@pytest.fixture
def sandbox(tmp_path):
    """Temporary directory acting as a project sandbox."""
    return str(tmp_path)


@pytest.fixture
def sandbox_with_file(sandbox):
    """Sandbox with a pre-existing file."""
    path = os.path.join(sandbox, "hello.txt")
    with open(path, "w") as f:
        f.write("hello world\n")
    return sandbox
