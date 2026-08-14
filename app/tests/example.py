from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Customer,Account
test_wrong_custmor = {
    "name": "test",
    "email": "[EMAIL_ADDRESS]",
    "phone": "cjknclsjdnc"
}


test_correct_custmor = {
    "name": "test",
    "email": "test@example.com",
    "phone": "1234567890"
}

test_correct_custmor1 = {
    "name": "test1",
    "email": "test1@example.com",
    "phone": "1234567891"
}


async def create_customer(session:AsyncSession):
    session.add(Customer(**test_correct_custmor))
    session.add(Customer(**test_correct_custmor1))

    await session.commit()


DEFAULT_PASSWORD = "StrongPass123!"


async def register_customer(async_client, customer=None):
    payload = customer or test_correct_custmor
    response = await async_client.post("/customers/customers", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


async def open_account(async_client, customer_id, account_type="SAVINGS"):
    response = await async_client.post(
        "/accounts/create",
        json={"customer_id": str(customer_id), "account_type": account_type},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def register_login(async_client, customer_id, password=DEFAULT_PASSWORD):
    response = await async_client.post(
        "/user/create",
        json={"customer_id": str(customer_id), "password": password},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def login(async_client, email, password=DEFAULT_PASSWORD):
    response = await async_client.post(
        "/user/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


async def auth_headers(async_client, email, password=DEFAULT_PASSWORD):
    token = await login(async_client, email, password)
    return {"Authorization": f"Bearer {token}"}


async def onboard_customer(
    async_client, customer=None, account_type="SAVINGS", password=DEFAULT_PASSWORD
):
    """Creates a customer, opens an account for them, registers login
    credentials and returns (customer, account, auth_headers)."""
    customer_data = await register_customer(async_client, customer)
    account_data = await open_account(async_client, customer_data["id"], account_type)
    await register_login(async_client, customer_data["id"], password)
    headers = await auth_headers(async_client, customer_data["email"], password)
    return customer_data, account_data, headers