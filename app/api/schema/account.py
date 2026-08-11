from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from database.models import AccountType

class AccountCreate(BaseModel):
    customer_id: UUID
    account_type: AccountType
  


class AccountResponse(BaseModel):
    account_number: str
    account_type: AccountType
    name:str
    balance:float
    status:str
    created_at:datetime

class MyAccountResponse(BaseModel):
    account_number: str
    account_type: AccountType
    name:str
    balance:float
    status:str
   
