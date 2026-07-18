from fastapi import FastAPI,HTTPException
from scalar_fastapi import get_scalar_api_reference
from schema import DepositTransaction, WithdrawalTransaction, TransferTransaction
from pydantic import BaseModel
data = {
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

app = FastAPI()


@app.post("/deposit")
async def deposit(transaction: DepositTransaction):
    account_number = transaction.account_number
    if account_number not in data:
        raise HTTPException(status_code=404, detail="Account not found")
    data[account_number]["amount"] += transaction.amount
    return {"message": "Deposit successful", "new_balance": data[account_number]["amount"]}

@app.post("/withdraw")
async def withdraw(transaction: WithdrawalTransaction):
    account_number = transaction.account_number
    if account_number not in data:
        raise HTTPException(status_code=404, detail="Account not found")
    if data[account_number]["amount"] < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    data[account_number]["amount"] -= transaction.amount
    return {"message": "Withdrawal successful", "new_balance": data[account_number]["amount"]}

@app.post("/transfer")
async def transfer(transaction: TransferTransaction):
    source_account_number = transaction.source_account_number
    target_account_number = transaction.target_account_number
    if source_account_number not in data:
        raise HTTPException(status_code=404, detail="Source account not found")
    if target_account_number not in data:
        raise HTTPException(status_code=404, detail="Target account not found")
    if data[source_account_number]["amount"] < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    data[source_account_number]["amount"] -= transaction.amount
    data[target_account_number]["amount"] += transaction.amount
    return {"message": "Transfer successful", "new_balance": data[source_account_number]["amount"], "target_new_balance": data[target_account_number]["amount"]}

@app.get("/scalar",include_in_schema=False)
async def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )