"""Project code."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lego_workflows.components import (
        CommandComponent,
        DomainEvent,
        R,
        T,
    )
    from lego_workflows.transactions import TransactionCommiter


def _commit_if_transaction_commiter(
    transaction_commiter: TransactionCommiter[T] | None, state_changes: list[T]
) -> None:
    if transaction_commiter is not None:
        transaction_commiter.commit_transaction(state_changes=state_changes)


async def run_and_collect_events(
    cmd: CommandComponent[R, T],
    transaction_commiter: TransactionCommiter[T] | None,
) -> tuple[R, list[DomainEvent]]:
    """Run command and collect events."""
    state_changes: list[T] = []
    events: list[DomainEvent] = []

    result = await cmd.run(state_changes=state_changes, events=events)
    _commit_if_transaction_commiter(
        transaction_commiter=transaction_commiter, state_changes=state_changes
    )
    return (result, events)


async def _publish_events(events: list[DomainEvent]) -> None:
    await asyncio.gather(
        *(event.publish() for event in events), return_exceptions=False
    )


async def execute(
    cmd: CommandComponent[R, T], transaction_commiter: TransactionCommiter[T] | None
) -> R:
    """Execute workflow and publish events."""
    result, events = await run_and_collect_events(
        cmd=cmd,
        transaction_commiter=transaction_commiter,
    )

    await _publish_events(events=events)

    return result
