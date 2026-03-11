from dataclasses import dataclass
from typing import Callable


@dataclass
class Workflow:
    id: str
    description: str
    system_prompt: str
    build_prompt: Callable[[dict], str]
    allowed_tools: list[str]
