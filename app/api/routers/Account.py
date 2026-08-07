from fastapi import APIRouter
from api.dependencies import accountServiceDep
from api.schema.account import AccountCreate,AccountResponse

router=APIRouter(
    prefix="/accounts",
    tags=["Account"]
)

@router.post("/accounts",response_model=AccountResponse)
async def create_account(account:AccountCreate,service:accountServiceDep):
    return await service.create_account(account)



@router.get("/accounts/{account_number}",response_model=AccountResponse)
async def get_account(account_number:str,service:accountServiceDep):
    return await service.get_account(account_number)