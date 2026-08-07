from api.schema.TransactionResponse import DepositTransactionResponse, WithdrawalTransactionResponse, TransferTransactionResponse
from fastapi import HTTPException, status
from sqlmodel import select

from api.schema.Transaction import DepositTransaction, TransactionType, WithdrawalTransaction, TransferTransaction
from database.models import Account, Transaction
from .BaseService import BaseService


class TransactionService(BaseService):

    def __init__(self, session):
        super().__init__(Transaction, session)

    async def deposit(self, transaction: DepositTransaction):
        t=transaction.model_dump()
        statement = select(Account).where(
            Account.account_number == t["account_number"]
        )
        result = await self.session.execute(statement)
        account = result.scalar_one_or_none()

        if not account :
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        if account.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is not active",
            )

        db_transaction = Transaction(
            account_number=account.account_number,
            amount=t["amount"],
            transaction_type=TransactionType.DEPOSIT.value,
        )
        await self._create(db_transaction)

        account.balance += t["amount"]
        await self._update(account)

        return DepositTransactionResponse(
            account_number=account.account_number,
            amount=t["amount"],
            description=t["description"],
            balance=account.balance
        )

    async def withdraw(self, transaction: WithdrawalTransaction):
        t=transaction.model_dump()
        statement = select(Account).where(
            Account.account_number == t["account_number"]
        )
        result = await self.session.execute(statement)
        account = result.scalar_one_or_none()

        if not account :
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        if account.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is not active",
            )
        if account.balance < t["amount"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance",
            )

        db_transaction = Transaction(
            account_number=account.account_number,
            amount=t["amount"],
            transaction_type=TransactionType.WITHDRAWAL.value,
        )
        await self._create(db_transaction)

        account.balance -= t["amount"]
        await self._update(account)

        return WithdrawalTransactionResponse(
            account_number=account.account_number,
            amount=t["amount"],
            description=t["description"],
            balance=account.balance
        )

    async def transfer(self, transaction: TransferTransaction) -> TransferTransactionResponse:
        if transaction.source_account_number == transaction.target_account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer funds to the same account",
            )

        stmt_source = select(Account).where(
                Account.account_number == transaction.source_account_number
            )
        stmt_dest = select(Account).where(
                Account.account_number == transaction.target_account_number
            )

        res_source = await self.session.execute(stmt_source)
        res_dest = await self.session.execute(stmt_dest)

        source_account = res_source.scalar_one_or_none()
        dest_account = res_dest.scalar_one_or_none()

        if not source_account or not dest_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or destination account not found",
            )

        if source_account.status != "ACTIVE" or dest_account.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or both accounts are not active",
            )

        if source_account.balance < transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance",
            )

        source_account.balance -= transaction.amount
        dest_account.balance += transaction.amount

        await self._update(source_account)
        await self._update(dest_account)

        db_transaction = Transaction(
            account_number=source_account.account_number,
            amount=transaction.amount,
            transaction_type=TransactionType.TRANSFER.value,
        )
        await self._create(db_transaction)

        return TransferTransactionResponse(
            source_account_number=source_account.account_number,
            target_account_number=dest_account.account_number,
            amount=transaction.amount,
            description=transaction.description,
            balance=source_account.balance,
        )