from .BaseService import BaseService
from api.schema.Customer import CustomerCreate, CustomerResponse, CustomerUpdate
from database.models import Customer
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


class CustomerService(BaseService):
    def __init__(self, session):
        super().__init__(Customer, session)

    async def create_customer(self, customer: CustomerCreate):
        existing = await self.session.execute(
            select(Customer.email, Customer.phone).where(
                or_(
                    Customer.email == customer.email,
                    Customer.phone == customer.phone,
                )
            ).limit(1)
        )
        row = existing.first()
        if row:
            if row.email == customer.email:
                raise HTTPException(status_code=400, detail="Email already exists")
            raise HTTPException(status_code=400, detail="Phone already exists")

        try:
            return await self._create(Customer(**customer.model_dump()))
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="Email or phone already exists")