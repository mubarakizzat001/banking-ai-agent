from pydantic import BaseModel

class BaseTransaction(BaseModel):
    amount: float
    description: str

class DepositTransaction(BaseTransaction):
     account_number: int

class WithdrawalTransaction(BaseTransaction):
     account_number: int

class TransferTransaction(BaseTransaction):
    source_account_number: int
    target_account_number: int
