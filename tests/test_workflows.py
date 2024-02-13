from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger
from uuid import UUID, uuid4

import pytest

import lego_workflows
from lego_workflows.components import Command, DomainError, DomainEvent, Response

logger = getLogger(__name__)


@dataclass(frozen=True)
class OpenBankAccountResponse(Response):
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


@dataclass(frozen=True)
class OpenBankAccountCommand(Command[OpenBankAccountResponse, str]):
    name: str
    initial_balance: int

    async def run(
        self, state_changes: list[str], events: list[DomainEvent]
    ) -> OpenBankAccountResponse:
        account_id = uuid4()
        balance_after_charge = self.initial_balance - 30
        if balance_after_charge < 0:
            raise NotEnoughFoundsError(initial_balance=self.initial_balance)

        state_changes.append("Insert account record")
        events.append(BankAccountOpened(account_id=account_id))
        return OpenBankAccountResponse(
            account_id=account_id,
            name=self.name,
            initial_balance=balance_after_charge,
        )


async def test_execute() -> None:
    result = await lego_workflows.execute(
        cmd=OpenBankAccountCommand(name="Peter", initial_balance=50),
        transaction_commiter=None,
    )
    assert result.initial_balance == 20  # noqa: PLR2004
    assert result.name == "Peter"


async def test_run_command_and_collect_events() -> None:
    result, events = await lego_workflows.run_and_collect_events(
        cmd=OpenBankAccountCommand(name="Peter", initial_balance=40),
        transaction_commiter=None,
    )
    assert result.initial_balance == 10  # noqa: PLR2004
    assert len(events) == 1
    assert isinstance(events[0], BankAccountOpened)


async def test_execute_with_failure() -> None:
    with pytest.raises(NotEnoughFoundsError):
        await lego_workflows.execute(
            cmd=OpenBankAccountCommand(name="Peter", initial_balance=10),
            transaction_commiter=None,
        )
