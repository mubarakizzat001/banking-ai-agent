
from service.Transaction import TransactionService
from fastapi import APIRouter, HTTPException
from ..schema.Transaction import DepositTransaction, WithdrawalTransaction, TransferTransaction,JWTTransaction
from ..schema.TransactionResponse import DepositTransactionResponse, WithdrawalTransactionResponse, TransferTransactionResponse,JWTTransactionResponse
from api.dependencies import transactionServiceDep,activeuserdep


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


@router.post("/transfer_from_my_account",response_model=JWTTransactionResponse)
async def transfer_from_my_account(
    transaction: JWTTransaction,
    service:transactionServiceDep,
    customer: activeuserdep
    ):
    return await service.transfer_from_my_account(transaction,customer)
