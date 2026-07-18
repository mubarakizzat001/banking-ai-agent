
from service.Transaction import ServiceTransaction
from fastapi import APIRouter, HTTPException
from ..schema.Transaction import DepositTransaction, WithdrawalTransaction, TransferTransaction
from ..schema.TransactionResponse import DepositTransactionResponse, WithdrawalTransactionResponse, TransferTransactionResponse



app = APIRouter(prefix="/transactions", tags=["Transactions"])
service = ServiceTransaction()

@app.post("/deposit",response_model=DepositTransactionResponse)
async def deposit(transaction: DepositTransaction):
   return service.deposit(transaction)

@app.post("/withdraw",response_model=WithdrawalTransactionResponse)
async def withdraw(transaction: WithdrawalTransaction):
   return service.withdraw(transaction)

@app.post("/transfer",response_model=TransferTransactionResponse)
async def transfer(transaction: TransferTransaction):
   return service.transfer(transaction)
