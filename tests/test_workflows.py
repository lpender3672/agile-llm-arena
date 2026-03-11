import pytest

from workflows import WORKFLOWS, Workflow
from workflows.impl_first import IMPL_FIRST
from workflows.iterative import ITERATIVE
from workflows.mutation_aware import MUTATION_AWARE
from workflows.tdd import TDD


SAMPLE_SPEC = {
    "name": "ring_buffer",
    "description": "Fixed-size circular buffer",
    "module": "ring_buffer",
    "file_tree": "src/ring_buffer.c\nsrc/ring_buffer.h\n",
    "spec": "Implement push/pop with overflow handling.",
}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def test_workflows_registry_has_expected_ids():
    assert set(WORKFLOWS.keys()) == {"tdd", "impl_first", "iterative", "mutation_aware"}


def test_all_workflows_are_workflow_instances():
    for w in WORKFLOWS.values():
        assert isinstance(w, Workflow)


def test_workflow_ids_match_registry_keys():
    for key, w in WORKFLOWS.items():
        assert w.id == key


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("workflow_id", list(WORKFLOWS.keys()))
def test_build_prompt_returns_non_empty_string(workflow_id):
    prompt = WORKFLOWS[workflow_id].build_prompt(SAMPLE_SPEC)
    assert isinstance(prompt, str)
    assert len(prompt) > 50


@pytest.mark.parametrize("workflow_id", list(WORKFLOWS.keys()))
def test_build_prompt_contains_module_name(workflow_id):
    prompt = WORKFLOWS[workflow_id].build_prompt(SAMPLE_SPEC)
    assert "ring_buffer" in prompt


@pytest.mark.parametrize("workflow_id", list(WORKFLOWS.keys()))
def test_build_prompt_contains_spec_description(workflow_id):
    prompt = WORKFLOWS[workflow_id].build_prompt(SAMPLE_SPEC)
    assert SAMPLE_SPEC["description"] in prompt


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("workflow_id", list(WORKFLOWS.keys()))
def test_system_prompts_non_empty(workflow_id):
    assert len(WORKFLOWS[workflow_id].system_prompt) > 10


# ---------------------------------------------------------------------------
# Allowed tools / skill sets
# ---------------------------------------------------------------------------

def test_all_workflows_have_run_tests():
    for w in WORKFLOWS.values():
        assert "RunTests" in w.allowed_tools, f"{w.id} missing RunTests"


def test_all_workflows_have_base_skills():
    for w in WORKFLOWS.values():
        for skill in ("Read", "Write", "Bash"):
            assert skill in w.allowed_tools, f"{w.id} missing {skill}"


def test_mutation_aware_has_run_mutation():
    assert "RunMutation" in MUTATION_AWARE.allowed_tools


def test_base_workflows_do_not_have_run_mutation():
    for w in [TDD, IMPL_FIRST, ITERATIVE]:
        assert "RunMutation" not in w.allowed_tools, f"{w.id} should not have RunMutation"
