"""Transaction utilities."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic

from lego_workflows.components import T


class TransactionCommiter(ABC, Generic[T]):
    """Commit transaction."""

    @abstractmethod
    def commit_transaction(self, state_changes: list[T]) -> None:
        """Commit operations in state changes as transaction against database."""
        raise NotImplementedError
