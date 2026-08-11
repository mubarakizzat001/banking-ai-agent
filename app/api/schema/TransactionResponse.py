
from pydantic import BaseModel, Field
from database.models import AccountType

class TransactionResponse(BaseModel):
    amount: float = Field(..., description="Amount cannot be empty")
    description: str = Field(..., description="Description cannot be empty")
    

class DepositTransactionResponse(TransactionResponse):
   account_number: str = Field(..., description="Account number cannot be empty")
   balance: float = Field(..., description="Balance cannot be empty")
class WithdrawalTransactionResponse(TransactionResponse):
    account_number: str = Field(..., description="Account number cannot be empty")
    balance: float = Field(..., description="Balance cannot be empty")

class TransferTransactionResponse(TransactionResponse):
    source_account_number: str = Field(..., description="Source account number cannot be empty")
    target_account_number: str = Field(..., description="Target account number cannot be empty")


#_____________________________transcation with jwt_______________________  

class JWTTransactionResponse(TransactionResponse):
    target_account:str
    account_type:AccountType
