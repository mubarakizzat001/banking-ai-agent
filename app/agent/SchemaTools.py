from pydantic import BaseModel,Field
from database.models import AccountType

class BaseSchema(BaseModel):
    account_type:AccountType =Field(
        description="account type of the customer"
    )


class CheckBalanceSchema(BaseSchema):
    pass

class CloseAccountSchema(BaseSchema):
    pass

class TransferSchema(BaseSchema):
    target_account: str = Field(description="The recipient's account number.")
    amount: float = Field(gt=0, description="Amount to transfer, must be greater than 0.")
    description: str = Field(description="A short reason/description for the transfer.")

