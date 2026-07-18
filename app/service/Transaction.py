from fastapi import HTTPException
from api.schema.Transaction import DepositTransaction, WithdrawalTransaction, TransferTransaction
   
account_data = {
    125 : {
"account_number": 125,
"amount": 1000.0,
    },
    126: {
"account_number": 126,
"amount": 500.0
    },
    127: {
"account_number": 127,
"amount": 0

}}

class ServiceTransaction:
 


    def deposit(self, transaction: DepositTransaction):
        account_number = transaction.account_number
        if account_number not in account_data:
            raise HTTPException(status_code=404, detail="Account not found")
        account_data[account_number]["amount"] += transaction.amount
        return {
            "account_number": account_data[account_number]["account_number"],
            "amount": transaction.amount,
            "balance": account_data[account_number]["amount"],
            "description": transaction.description,
        }
    def withdraw(self, transaction: WithdrawalTransaction):
        account_number = transaction.account_number
        if account_number not in account_data:
            raise HTTPException(status_code=404, detail="Account not found")
        if account_data[account_number]["amount"] < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        account_data[account_number]["amount"] -= transaction.amount
        return {
            "account_number": account_data[account_number]["account_number"],
            "amount": transaction.amount,
            "balance": account_data[account_number]["amount"],
        "description": transaction.description,
    }
    def transfer(self, transaction: TransferTransaction):
        source_account_number = transaction.source_account_number
        target_account_number = transaction.target_account_number
        if source_account_number not in account_data:
            raise HTTPException(status_code=404, detail="Source account not found")
        if target_account_number not in account_data:
            raise HTTPException(status_code=404, detail="Target account not found")
        if account_data[source_account_number]["amount"] < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        account_data[source_account_number]["amount"] -= transaction.amount
        account_data[target_account_number]["amount"] += transaction.amount
        return {
            "source_account_number": account_data[source_account_number]["account_number"],
            "target_account_number": account_data[target_account_number]["account_number"],
            "balance": account_data[source_account_number]["amount"],
            "amount": transaction.amount,
            "description": transaction.description,
        }
