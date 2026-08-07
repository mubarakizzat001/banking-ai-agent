from service.CustomerService import CustomerService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from database.session import get_session



sessionDep=Annotated[AsyncSession,Depends(get_session)]

def get_customer_service(session:sessionDep):
    return CustomerService(session=session)

servicesDep=Annotated[CustomerService,Depends(get_customer_service)]