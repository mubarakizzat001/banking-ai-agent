from dns import rdata
from database.models import AccountType
from .SchemaTools import CheckBalanceSchema,CloseAccountSchema,TransferSchema
from langchain_core.tools import StructuredTool
from .client import get_client



async def _request(
    method:str,
    url:str,
    headers:dict,
    **kwargs
    
)->str:
    client = get_client()
    response = await client.request(method,url,headers=headers,**kwargs)
    if response.status_code !=200:
        detail = response.json().get("detail", response.text)
        return f"Request failed ({response.status_code}): {detail}"
    return response.json()

def build_tools(headers:dict)->list[StructuredTool]:
    """Build a list of structured tools for the agent."""
    
    async def check_balance(account_type:AccountType)->str:
           data = await _request(
            "POST",
            "/accounts/my-accounts",
            headers,
            params={"account_type": account_type.value},
            )
           if isinstance(data, str):
            return data
           return (
            f"Account {data['account_number']} ({data['account_type']}): "
            f"balance {data['balance']}, status {data['status']}."
            )

    async def transfer_money(
        target_account:str,
        account_type:AccountType,
        amount:float,
        description:str
    
    ) -> str:
        data =await _request(
            "POST",
            "/transactions/transfer_from_my_account",
            headers,
            json={
                "target_account":target_account,
                "account_type":account_type.value,
                "amount":amount,
                "description":description
            }
        )
        if isinstance(data, str):
            return data
        return (
            f"Transferred {data['amount']} from the customer's {data['account_type']} "
            f"account to {data['target_account']}. Description: {data['description']}."
        )

    async def close_account(
        account_type:AccountType
    ) -> str:
        data = await _request(
            "POST",
            "/accounts/close-my-account",
            headers,
            params={"account_type": account_type.value}
        )
        if isinstance(data, str):
            return data
        return (
            f"Closed account {data['account_number']} ({data['account_type']}) "
            f"due to inactivity."
        )
    
    return[
        StructuredTool.from_function(
            coroutine=check_balance,
            name="check_balance",
            description="Check the balance of a specific account",
            args_schema=CheckBalanceSchema,
        ),
        StructuredTool.from_function(
            coroutine=transfer_money,
            name="transfer_money",
            description=(
                "Transfer money from one of the customer's own accounts to another "
                "account number. The source account is always the authenticated "
                "customer's own account - never ask for a source account number."
            ),
            args_schema=TransferSchema,
        ),
        StructuredTool.from_function(
            coroutine=close_account,
            name="close_account",
            description="Close an account if it is inactive or the user requests.",
            args_schema=CloseAccountSchema,
        ),
    ]
