from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger
from typing import TypeAlias
from uuid import UUID, uuid4

from result import Err, Ok

import lego_workflows
from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)

logger = getLogger(__name__)


@dataclass(frozen=True)
class Response(ResponseComponent):
    account_id: UUID
    name: str
    initial_balance: int


@dataclass(frozen=True)
class BankAccountOpened(DomainEvent):
    account_id: UUID

    async def publish(self) -> None:
        logger.info(f"New bank account opened with ID {self.account_id!s}")  # noqa: G004


class NotEnoughFoundsError(DomainError):
    def __init__(self, initial_balance: int) -> None:
        super().__init__(f"{initial_balance:,} is not enough for opening an account.")


Errors: TypeAlias = NotEnoughFoundsError


@dataclass(frozen=True)
class Command(CommandComponent[Response, Errors]):
    name: str
    initial_balance: int

    async def run(
        self, events: list[DomainEvent]
    ) -> Ok[Response] | Err[NotEnoughFoundsError]:
        account_id = uuid4()
        balance_after_charge = self.initial_balance - 30
        if balance_after_charge < 0:
            return Err(NotEnoughFoundsError(initial_balance=self.initial_balance))

        events.append(BankAccountOpened(account_id=account_id))
        return Ok(
            Response(
                account_id=account_id,
                name=self.name,
                initial_balance=balance_after_charge,
            )
        )


async def test_execute() -> None:
    match await lego_workflows.run_and_collect_events(
        Command(name="Peter", initial_balance=50)
    ):
        case Ok((result, events)):
            assert result.initial_balance == 20  # noqa: PLR2004
            assert result.name == "Peter"
            await lego_workflows.publish_events(events=events)
        case Err():
            raise AssertionError


async def test_run_command_and_collect_events() -> None:
    match await lego_workflows.run_and_collect_events(
        cmd=Command(name="Peter", initial_balance=40),
    ):
        case Ok((result, events)):
            assert result.initial_balance == 10  # noqa: PLR2004
            assert len(events) == 1
            assert isinstance(events[0], BankAccountOpened)

            await lego_workflows.publish_events(events=events)
        case Err():
            raise AssertionError


async def test_execute_with_failure() -> None:
    match await lego_workflows.run_and_collect_events(
        cmd=Command(name="Peter", initial_balance=10),
    ):
        case Ok(_):
            raise AssertionError
        case Err(error):
            assert isinstance(error, NotEnoughFoundsError)
