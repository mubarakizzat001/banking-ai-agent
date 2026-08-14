import uuid

from .example import (
    register_customer,
    open_account,
    onboard_customer,
)

create_url = "/accounts/create"
get_url = "/accounts/account/{account_number}"
my_accounts_url = "/accounts/my-accounts"
close_account_url = "/accounts/close-my-account"


async def test_create_account_success(async_client):
    customer = await register_customer(async_client)

    response = await async_client.post(
        create_url,
        json={"customer_id": customer["id"], "account_type": "SAVINGS"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["account_type"] == "SAVINGS"
    assert data["name"] == customer["name"]
    assert data["balance"] == 0
    assert data["status"] == "ACTIVE"
    assert "account_number" in data


async def test_create_account_customer_not_found(async_client):
    response = await async_client.post(
        create_url,
        json={"customer_id": str(uuid.uuid4()), "account_type": "SAVINGS"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


async def test_create_account_invalid_account_type(async_client):
    customer = await register_customer(async_client)

    response = await async_client.post(
        create_url,
        json={"customer_id": customer["id"], "account_type": "NOT_A_TYPE"},
    )

    assert response.status_code == 422


async def test_create_account_missing_field(async_client):
    response = await async_client.post(create_url, json={"account_type": "SAVINGS"})

    assert response.status_code == 422


async def test_get_account_success(async_client):
    customer = await register_customer(async_client)
    account = await open_account(async_client, customer["id"])

    response = await async_client.get(get_url.format(account_number=account["account_number"]))

    assert response.status_code == 200
    data = response.json()
    assert data["account_number"] == account["account_number"]
    assert data["name"] == customer["name"]


async def test_get_account_not_found(async_client):
    response = await async_client.get(get_url.format(account_number="00000000"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


async def test_my_accounts_success(async_client):
    customer, account, headers = await onboard_customer(async_client, account_type="SAVINGS")

    response = await async_client.post(
        my_accounts_url,
        params={"account_type": "SAVINGS"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["account_number"] == account["account_number"]
    assert data["account_type"] == "SAVINGS"


async def test_my_accounts_no_matching_account(async_client):
    _customer, _account, headers = await onboard_customer(async_client, account_type="SAVINGS")

    response = await async_client.post(
        my_accounts_url,
        params={"account_type": "CURRENT"},
        headers=headers,
    )

    assert response.status_code == 404


async def test_my_accounts_requires_auth(async_client):
    response = await async_client.post(
        my_accounts_url,
        params={"account_type": "SAVINGS"},
    )

    assert response.status_code == 401


async def test_my_accounts_invalid_token(async_client):
    response = await async_client.post(
        my_accounts_url,
        params={"account_type": "SAVINGS"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


async def test_close_my_account_success(async_client):
    _customer, account, headers = await onboard_customer(async_client, account_type="SAVINGS")

    response = await async_client.post(
        close_account_url,
        params={"account_type": "SAVINGS"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "closed"

    check = await async_client.get(get_url.format(account_number=account["account_number"]))
    assert check.json()["status"] == "closed"


async def test_close_my_account_with_balance_fails(async_client):
    customer, account, headers = await onboard_customer(async_client, account_type="SAVINGS")

    await async_client.post(
        "/transactions/deposit",
        json={
            "account_number": account["account_number"],
            "amount": 100,
            "description": "seed balance",
        },
    )

    response = await async_client.post(
        close_account_url,
        params={"account_type": "SAVINGS"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "not active or balance is not 0" in response.json()["detail"]


async def test_close_my_account_requires_auth(async_client):
    response = await async_client.post(
        close_account_url,
        params={"account_type": "SAVINGS"},
    )

    assert response.status_code == 401


async def test_close_my_account_no_matching_account(async_client):
    _customer, _account, headers = await onboard_customer(async_client, account_type="SAVINGS")

    response = await async_client.post(
        close_account_url,
        params={"account_type": "CURRENT"},
        headers=headers,
    )

    assert response.status_code == 404
