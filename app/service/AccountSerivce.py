from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import select

from .BaseService import BaseService
from database.models import Account, AccountType,Customer
from api.schema.account import AccountCreate

class AccountService(BaseService):

    def __init__(self, session):
        super().__init__(Account, session)

    async def create_account(self, account:AccountCreate):
        customer = await self._get(Customer,account.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Customer not found"
            )

        account = Account(
            customer_id=customer.id,
            name=customer.name,
            account_type=account.account_type
        )
        return await self._create(account)

    async def get_account(self, account_number: str):
        statement = select(Account).where(Account.account_number == account_number)
        result = await self.session.execute(statement)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return account
    async def close_account(self, customer_id: UUID, account_type: AccountType):
        statement = select(Account).where(
            Account.customer_id == customer_id,
            Account.account_type == account_type.value
        )
        result = await self.session.execute(statement)
        account = result.scalars().first()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specified account not found",
        )

        if account.status != "ACTIVE" or account.balance != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is not active or balance is not 0",
            )

        account.status = "closed"
        await self._update(account)
        return account

    async def get_my_accounts(self, customer_id: UUID, account_type: AccountType):
        statement = select(Account).where(
            Account.customer_id == customer_id,
            Account.account_type == account_type.value
        )
        result = await self.session.execute(statement)
        account = result.scalars().all()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specified account not found",
        )

        return account[-1]

