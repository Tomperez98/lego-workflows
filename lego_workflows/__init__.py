"""Project code."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from result import Err

if TYPE_CHECKING:
    from lego_workflows.components import (
        CommandComponent,
        DomainEvent,
        R,
    )


async def run_and_collect_events(
    cmd: CommandComponent[R],
) -> tuple[R, list[DomainEvent]]:
    """Run command and collect events."""
    events: list[DomainEvent] = []

    result = await cmd.run(events=events)
    if isinstance(result, Err):
        raise result.err()

    return (result.unwrap(), events)


async def publish_events(events: list[DomainEvent]) -> None:
    """Publish collected events."""
    await asyncio.gather(
        *(event.publish() for event in events), return_exceptions=False
    )
