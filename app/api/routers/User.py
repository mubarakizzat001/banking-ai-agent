from typing import Annotated
from fastapi import APIRouter,Depends
from fastapi.security import OAuth2PasswordRequestForm
from api.dependencies import userServiceDep
from api.schema.User import UserCreate,UserResponse

router = APIRouter(tags=["User"],prefix="/user")

@router.post("/create" , status_code=201,response_model=UserResponse)
async def create_user(user:UserCreate,service:userServiceDep):
    return await service.create_user(user)

@router.get("/get/{email}" , response_model=UserResponse)
async def get_user(email:str,service:userServiceDep):
    return await service.get_user(email)
@router.post("/login",response_model=UserResponse)
async def login(requestform:Annotated[OAuth2PasswordRequestForm,Depends()],service:userServiceDep):
    return await service.login(requestform.username,requestform.password)