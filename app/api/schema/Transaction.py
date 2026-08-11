from enum import Enum
from pydantic import BaseModel, Field
from database.models import AccountType


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"

    
class BaseTransaction(BaseModel):
    amount: float = Field(gt=0, description="Amount must be greater than 0")
    description: str = Field(..., description="Description cannot be empty")

class DepositTransaction(BaseTransaction):
    account_number: str = Field(..., description="Account number cannot be empty")

class WithdrawalTransaction(BaseTransaction):
    account_number: str = Field(..., description="Account number cannot be empty")

class TransferTransaction(BaseTransaction):
    source_account_number: str = Field(..., description="Source account number cannot be empty")
    target_account_number: str = Field(..., description="Target account number cannot be empty")


#_____________________________transcation with jwt_______________________

class JWTTransaction(BaseTransaction):
    target_account:str
    account_type:AccountType

