"""Workflow definition components."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass(frozen=True)
class Response:
    """Workflow response data."""


@dataclass(frozen=True)
class DomainEvent(ABC):
    """Worflow event."""

    @abstractmethod
    async def publish(self) -> None:
        """Publish event."""


class DomainError(Exception):
    """Raised when a user violates a business rule."""


T = TypeVar("T")
R = TypeVar("R", bound=Response)


@dataclass(frozen=True)
class Command(Generic[R, T]):
    """Workflow input data."""

    @abstractmethod
    async def run(self, state_changes: list[T], events: list[DomainEvent]) -> R:
        """Execute workflow."""
        raise NotImplementedError
