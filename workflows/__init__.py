from .base import Workflow
from .impl_first import IMPL_FIRST
from .iterative import ITERATIVE
from .mutation_aware import MUTATION_AWARE
from .tdd import TDD

WORKFLOWS: dict[str, Workflow] = {w.id: w for w in [TDD, IMPL_FIRST, ITERATIVE, MUTATION_AWARE]}

__all__ = ["WORKFLOWS", "Workflow", "TDD", "IMPL_FIRST", "ITERATIVE", "MUTATION_AWARE"]
