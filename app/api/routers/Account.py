from database.models import AccountType
from fastapi import APIRouter
from api.dependencies import accountServiceDep,activeuserdep
from api.schema.account import AccountCreate,AccountResponse,MyAccountResponse

router=APIRouter(
    prefix="/accounts",
    tags=["Account"]
)

@router.post("/create",response_model=AccountResponse)
async def create_account(account:AccountCreate,service:accountServiceDep):
    return await service.create_account(account)

@router.post("/my-accounts", response_model=MyAccountResponse)
async def get_customer_account(service:accountServiceDep,
    customer: activeuserdep,
    account_type: AccountType
    ):
  return await service.get_my_accounts(customer.id,account_type)

@router.post("/close-my-account")
async def close_my_account(
    service:accountServiceDep,
    customer: activeuserdep,
    account_type: AccountType
    
    ):
    return await service.close_account(
        customer_id=customer.id,
        account_type=account_type
        )

@router.get("/account/{account_number}",response_model=AccountResponse)
async def get_account(account_number:str,service:accountServiceDep):
    return await service.get_account(account_number)
