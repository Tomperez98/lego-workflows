"""Project code."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from result import Err, Ok, Result

if TYPE_CHECKING:
    from lego_workflows.components import CommandComponent, DomainEvent, E, R


async def run_and_collect_events(
    cmd: CommandComponent[R, E],
) -> Result[tuple[R, list[DomainEvent]], E]:
    """Run command and collect events."""
    events: list[DomainEvent] = []

    match await cmd.run(events=events):
        case Ok(result):
            return Ok((result, events))
        case Err(error):
            return Err(error)
    raise NotImplementedError


async def publish_events(events: list[DomainEvent]) -> None:
    """Publish collected events."""
    await asyncio.gather(
        *(event.publish() for event in events), return_exceptions=False
    )
