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

@router.get("/my-accounts", response_model=MyAccountResponse)
async def get_customer_account(customer: activeuserdep):
  return customer.accounts[-1]


@router.get("/account/{account_number}",response_model=AccountResponse)
async def get_account(account_number:str,service:accountServiceDep):
    return await service.get_account(account_number)
