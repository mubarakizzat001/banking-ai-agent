from typing import Annotated
from fastapi import APIRouter,Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from api.dependencies import userServiceDep,get_access_token
from api.schema.User import UserCreate,UserResponse
from database.redis import add_tokens_to_blacklist
router = APIRouter(tags=["User"],prefix="/user")

@router.post("/create" , status_code=201,response_model=UserResponse)
async def create_user(user:UserCreate,service:userServiceDep):
    return await service.create_user(user)

@router.get("/get/{email}" , response_model=UserResponse)
async def get_user(email:str,service:userServiceDep):
    return await service.get_user(email)




@router.post("/login")
async def login(
    requestform:Annotated[OAuth2PasswordRequestForm,Depends()],
    service:userServiceDep
    ):
    token=await service.login(requestform.username,requestform.password)
    return {"access_token":token,"token_type":"Bearer"}

@router.post("/logout")
async def logout(token:Annotated[str,Depends(get_access_token)]):
    await add_tokens_to_blacklist(token['jti'])
    return {"message":"Logged out successfully"}
