from service.CustomerService import CustomerService
from service.AccountSerivce import AccountService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from database.session import get_session



sessionDep=Annotated[AsyncSession,Depends(get_session)]

def get_customer_service(session:sessionDep):
    return CustomerService(session=session)

def get_account_service(session:sessionDep):
    return AccountService(session=session)

customerServiceDep=Annotated[CustomerService,Depends(get_customer_service)]
accountServiceDep=Annotated[AccountService,Depends(get_account_service)]