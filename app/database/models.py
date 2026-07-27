from datetime import datetime
from sqlmodel import SQLModel,Field



class transactions(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    account_number:str=Field(max_length=10,index=True)
    amount:float
    transaction_type:str=Field(max_length=20)
    timestamp:datetime=Field(default_factory=datetime.now)