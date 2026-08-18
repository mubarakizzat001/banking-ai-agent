from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from config import settingAI
from .tools import build_tools


SYSTEM_PROMPT = (
    "You are the banking assistant for {customer_name}, an authenticated customer. "
    "You can check the balance of, transfer money from, and close the customer's own "
    "accounts using the tools provided. You can only ever act on this customer's own "
    "accounts - the source account for transfers is always resolved automatically, "
    "never ask the customer for their own account number. Always ask for the "
    "account_type (SAVINGS, CURRENT, or SALARY) if the customer hasn't specified "
    "which account they mean. Confirm the result of any action clearly and concisely."
)


async def create_banking_agent(headers:dict,customer_name:str):
    llm = ChatOpenAI(
        api_key = settingAI.OPENROUTER_API_KEY,
        model = settingAI.OPENROUTER_MODEL,
        base_url = settingAI.OPENROUTER_BASE_URL,
        temperature = 0,
        streaming =True
    )
    tools = build_tools(headers=headers)

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT.format(customer_name=customer_name),
        
    )
    
