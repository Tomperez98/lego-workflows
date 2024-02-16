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


async def run_and_collect_events(
    cmd: CommandComponent[R, T],
) -> tuple[R, list[DomainEvent]]:
    """Run command and collect events."""
    state_changes: list[T] = []
    events: list[DomainEvent] = []

    result = await cmd.run(state_changes=state_changes, events=events)
    return (result, events)


async def _publish_events(events: list[DomainEvent]) -> None:
    await asyncio.gather(
        *(event.publish() for event in events), return_exceptions=False
    )


async def execute(cmd: CommandComponent[R, T]) -> R:
    """Execute workflow and publish events."""
    result, events = await run_and_collect_events(
        cmd=cmd,
    )

    await _publish_events(events=events)

    return result
