from service.CustomerService import CustomerService
from service.AccountSerivce import AccountService
from service.Transaction import TransactionService
from service.UserService import UserService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from database.session import get_session



sessionDep=Annotated[AsyncSession,Depends(get_session)]

def get_customer_service(session:sessionDep):
    return CustomerService(session=session)

def get_account_service(session:sessionDep):
    return AccountService(session=session)


def get_transaction_service(session:sessionDep):
    return TransactionService(session=session)

def get_user_service(session:sessionDep):
    return UserService(session=session)

customerServiceDep=Annotated[CustomerService,Depends(get_customer_service)]
accountServiceDep=Annotated[AccountService,Depends(get_account_service)]
transactionServiceDep=Annotated[TransactionService,Depends(get_transaction_service)]
userServiceDep=Annotated[UserService,Depends(get_user_service)]