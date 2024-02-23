"""Workflow definition components."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass(frozen=True)
class ResponseComponent:
    """Workflow response data."""


@dataclass(frozen=True)
class DomainEvent(ABC):
    """Worflow event."""

    @abstractmethod
    async def publish(self) -> None:
        """Publish event."""


class DomainError(Exception):
    """Raised when a user violates a business rule."""


R = TypeVar("R", bound=ResponseComponent)


@dataclass(frozen=True)
class CommandComponent(Generic[R]):
    """Workflow input data."""

    @abstractmethod
    async def run(self, events: list[DomainEvent]) -> R:
        """Execute workflow."""
        raise NotImplementedError
