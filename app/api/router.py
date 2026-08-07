from .routers import Customer,Account
from .routers import Transaction
from fastapi import APIRouter



master_router = APIRouter()

master_router.include_router(Transaction.router)
master_router.include_router(Customer.router)
master_router.include_router(Account.router)