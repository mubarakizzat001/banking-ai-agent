from sqlalchemy import select
from api.schema.User import UserCreate
from .BaseService import BaseService
from database.models import UserAccounts,Customer
from fastapi import HTTPException
import bcrypt
from utils import create_access_token


class UserService(BaseService):
    def __init__(self, session):
        super().__init__(UserAccounts, session)

    async def create_user(self,user:UserCreate):
        customer=await self._get(Customer,user.customer_id)
        if not customer:
            raise HTTPException(status_code=404,detail="Customer not found")
        hashed_password = bcrypt.hashpw(
            user.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode("utf-8")

        user_accounts = UserAccounts(
            **user.model_dump(exclude={"password"}),
            hash_password=hashed_password
        )
        await self._create(user_accounts)
        return {
            "id": user_accounts.id,
            "customer_id": user_accounts.customer_id
        }
    async def get_user(self,email:str):
        user = await self.session.execute(
            select(UserAccounts)
            .join(Customer, UserAccounts.customer_id == Customer.id)  
            .where(Customer.email == email)
        )
        user=user.scalars().first()
        if not user:
            raise HTTPException(status_code=404,detail="User not found")
        return user

    async def login(self,email:str,password:str):
        user=await self.get_user(email)
        if bcrypt.checkpw(password.encode("utf-8"), user.hash_password.encode("utf-8")):
            return create_access_token({"id": str(user.id), "customer_id": str(user.customer_id)})
        else:
            raise HTTPException(status_code=401,detail="Invalid credentials")
            


        