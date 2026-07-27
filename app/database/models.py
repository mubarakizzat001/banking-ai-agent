from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import EmailStr
from sqlalchemy.dialects import postgresql
from sqlmodel import SQLModel, Field, Sequence, Column, String, Relationship



class AccountType(str, Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    SALARY = "salary"



class Customer(SQLModel, table=True):
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
            nullable=False
        )
    )
    name: str = Field(max_length=100, nullable=False)
    email: EmailStr = Field(max_length=100, nullable=False, unique=True)
    phone: str = Field(max_length=15, nullable=False)
    
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP(timezone=True),
            default=datetime.utcnow,
            nullable=False
        )
    )

   
    accounts: list["Account"] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


account_number_seq = Sequence("account_number_seq", start=10000000, increment=1)



class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    
    
    customer_id: UUID = Field(foreign_key="customer.id", nullable=False)
    
   
    customer: Customer | None = Relationship(back_populates="accounts")

    account_number: str = Field(
        sa_column=Column(
            String,
            account_number_seq,
            server_default=account_number_seq.next_value(),
            unique=True,
            nullable=False,
            index=True
        )
    )
    
    account_type: AccountType = Field(nullable=False)
    balance: float = Field(default=0.0)
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP(timezone=True),
            default=datetime.utcnow,
            nullable=False
        )
    )

class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_number: str = Field(max_length=20, nullable=False, index=True)
    amount: float = Field(nullable=False)
    transaction_type: str = Field(max_length=20, nullable=False)  # DEPOSIT, WITHDRAW, TRANSFER
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP(timezone=True),
            default=datetime.utcnow,
            nullable=False
        )
    )