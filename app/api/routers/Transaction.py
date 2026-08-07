
from service.Transaction import TransactionService
from fastapi import APIRouter, HTTPException
from ..schema.Transaction import DepositTransaction, WithdrawalTransaction, TransferTransaction
from ..schema.TransactionResponse import DepositTransactionResponse, WithdrawalTransactionResponse, TransferTransactionResponse
from api.dependencies import transactionServiceDep


router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/deposit",response_model=DepositTransactionResponse)
async def deposit(transaction: DepositTransaction,service:transactionServiceDep):
   return await service.deposit(transaction)

@router.post("/withdraw",response_model=WithdrawalTransactionResponse)
async def withdraw(transaction: WithdrawalTransaction,service:transactionServiceDep):
   return await service.withdraw(transaction)

@router.post("/transfer",response_model=TransferTransactionResponse)
async def transfer(transaction: TransferTransaction,service:transactionServiceDep):
   return await service.transfer(transaction)
