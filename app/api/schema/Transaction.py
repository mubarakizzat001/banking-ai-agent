from pydantic import BaseModel, Field

class BaseTransaction(BaseModel):
    amount: float = Field(gt=0, description="Amount must be greater than 0")
    description: str = Field(..., description="Description cannot be empty")

class DepositTransaction(BaseTransaction):
    account_number: int = Field(..., description="Account number cannot be empty")

class WithdrawalTransaction(BaseTransaction):
    account_number: int = Field(..., description="Account number cannot be empty")

class TransferTransaction(BaseTransaction):
    source_account_number: int = Field(..., description="Source account number cannot be empty")
    target_account_number: int = Field(..., description="Target account number cannot be empty")
