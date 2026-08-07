from api.dependencies import servicesDep
from api.schema.Customer import CustomerCreate,CustomerResponse,CustomerUpdate
from fastapi import APIRouter


router=APIRouter(
    prefix="/customers",
    tags=["Customer"]
)

@router.post("/customers",response_model=CustomerResponse)
async def create_customer(customer:CustomerCreate,servicesDep:servicesDep):
    return await servicesDep.create_customer(customer)
