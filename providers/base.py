from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    role: str  # "user" | "assistant"
    content: str


@dataclass
class RunResult:
    output: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    duration_seconds: float
    turns: int
    error: Optional[str] = None


class Provider(ABC):
    @abstractmethod
    async def run(
        self,
        prompt: str,
        system: str,
        cwd: str,
        max_tokens: int,
        allowed_tools: list[str],
    ) -> RunResult:
        ...
