"""Workflow definition components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from result import Result


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
E = TypeVar("E", bound=DomainError)


@dataclass(frozen=True)
class CommandComponent(Generic[R, E]):
    """Workflow input data."""

    @abstractmethod
    async def run(self, events: list[DomainEvent]) -> Result[R, E]:
        """Execute workflow."""
        raise NotImplementedError
