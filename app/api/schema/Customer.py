from pydantic import BaseModel,EmailStr
from uuid import UUID

class CustomerBase(BaseModel):
    name:str
    email:EmailStr
    phone:str


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id:UUID

