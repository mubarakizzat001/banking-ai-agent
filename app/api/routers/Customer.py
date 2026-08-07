from api.dependencies import customerServiceDep
from api.schema.Customer import CustomerCreate,CustomerResponse,CustomerUpdate
from fastapi import APIRouter


router=APIRouter(
    prefix="/customers",
    tags=["Customer"]
)

@router.post("/customers",response_model=CustomerResponse)
async def create_customer(customer:CustomerCreate,service:customerServiceDep):
    return await service.create_customer(customer)
