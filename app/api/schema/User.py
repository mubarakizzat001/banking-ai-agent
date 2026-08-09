from pydantic import BaseModel,EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    password: str
    customer_id: UUID

class UserResponse(BaseModel):
    id: UUID
    customer_id: UUID

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    

class UserUpdate(BaseModel):
    email: EmailStr
    password: str