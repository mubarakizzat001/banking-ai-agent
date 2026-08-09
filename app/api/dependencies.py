from core.security import oauth2_scheme
from utils import decode_access_token
from service.CustomerService import CustomerService
from service.AccountSerivce import AccountService
from service.Transaction import TransactionService
from service.UserService import UserService
from fastapi import Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from database.session import get_session
from database.redis import is_token_blacklisted



sessionDep=Annotated[AsyncSession,Depends(get_session)]

async def _get_access_token(token:str):
    data = decode_access_token(token)
    if await is_token_blacklisted(data['jti']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token is blacklisted")
    return data   
async def get_access_token(token:Annotated[str,Depends(oauth2_scheme)]):
    return await _get_access_token(token)
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