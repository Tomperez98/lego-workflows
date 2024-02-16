"""Workflow definition components."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel


class ResponseComponent(BaseModel):
    """Workflow response data."""


class DomainEvent(BaseModel, ABC):
    """Worflow event."""

    @abstractmethod
    async def publish(self) -> None:
        """Publish event."""


class DomainError(Exception):
    """Raised when a user violates a business rule."""


T = TypeVar("T")
R = TypeVar("R", bound=ResponseComponent)


class CommandComponent(BaseModel, Generic[R, T]):
    """Workflow input data."""

    @abstractmethod
    async def run(self, state_changes: list[T], events: list[DomainEvent]) -> R:
        """Execute workflow."""
        raise NotImplementedError
