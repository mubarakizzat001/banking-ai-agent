from .example import (
    test_correct_custmor,
    test_correct_custmor1,
    register_customer,
    open_account,
    onboard_customer,
)

deposit_url = "/transactions/deposit"
withdraw_url = "/transactions/withdraw"
transfer_url = "/transactions/transfer"
transfer_from_my_account_url = "/transactions/transfer_from_my_account"


async def _closed_account(async_client, account_type="SAVINGS"):
    """Onboards a customer and returns a CLOSED account plus its headers."""
    customer, account, headers = await onboard_customer(async_client, account_type=account_type)
    response = await async_client.post(
        "/accounts/close-my-account",
        params={"account_type": account_type},
        headers=headers,
    )
    assert response.status_code == 200
    return customer, account, headers


# _____________________________ deposit _______________________

async def test_deposit_success(async_client):
    customer = await register_customer(async_client)
    account = await open_account(async_client, customer["id"])

    response = await async_client.post(
        deposit_url,
        json={
            "account_number": account["account_number"],
            "amount": 100,
            "description": "salary",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 100
    assert data["account_number"] == account["account_number"]


async def test_deposit_account_not_found(async_client):
    response = await async_client.post(
        deposit_url,
        json={"account_number": "00000000", "amount": 100, "description": "salary"},
    )

    assert response.status_code == 404


async def test_deposit_inactive_account(async_client):
    _customer, account, _headers = await _closed_account(async_client)

    response = await async_client.post(
        deposit_url,
        json={
            "account_number": account["account_number"],
            "amount": 100,
            "description": "salary",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Account is not active"


async def test_deposit_negative_amount(async_client):
    customer = await register_customer(async_client)
    account = await open_account(async_client, customer["id"])

    response = await async_client.post(
        deposit_url,
        json={
            "account_number": account["account_number"],
            "amount": -50,
            "description": "salary",
        },
    )

    assert response.status_code == 422


async def test_deposit_missing_description(async_client):
    customer = await register_customer(async_client)
    account = await open_account(async_client, customer["id"])

    response = await async_client.post(
        deposit_url,
        json={"account_number": account["account_number"], "amount": 50},
    )

    assert response.status_code == 422


# _____________________________ withdraw _______________________

async def test_withdraw_success(async_client):
    customer = await register_customer(async_client)
    account = await open_account(async_client, customer["id"])
    await async_client.post(
        deposit_url,
        json={
            "account_number": account["account_number"],
            "amount": 100,
            "description": "seed",
        },
    )

    response = await async_client.post(
        withdraw_url,
        json={
            "account_number": account["account_number"],
            "amount": 40,
            "description": "atm",
        },
    )

    assert response.status_code == 200
    assert response.json()["balance"] == 60


async def test_withdraw_insufficient_balance(async_client):
    customer = await register_customer(async_client)
    account = await open_account(async_client, customer["id"])

    response = await async_client.post(
        withdraw_url,
        json={
            "account_number": account["account_number"],
            "amount": 40,
            "description": "atm",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance"


async def test_withdraw_account_not_found(async_client):
    response = await async_client.post(
        withdraw_url,
        json={"account_number": "00000000", "amount": 10, "description": "atm"},
    )

    assert response.status_code == 404


async def test_withdraw_inactive_account(async_client):
    _customer, account, _headers = await _closed_account(async_client)

    response = await async_client.post(
        withdraw_url,
        json={
            "account_number": account["account_number"],
            "amount": 10,
            "description": "atm",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Account is not active"


# _____________________________ transfer _______________________

async def test_transfer_success(async_client):
    source_customer = await register_customer(async_client, test_correct_custmor)
    target_customer = await register_customer(async_client, test_correct_custmor1)
    source_account = await open_account(async_client, source_customer["id"])
    target_account = await open_account(async_client, target_customer["id"])

    await async_client.post(
        deposit_url,
        json={
            "account_number": source_account["account_number"],
            "amount": 200,
            "description": "seed",
        },
    )

    response = await async_client.post(
        transfer_url,
        json={
            "source_account_number": source_account["account_number"],
            "target_account_number": target_account["account_number"],
            "amount": 75,
            "description": "rent",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["source_account_number"] == source_account["account_number"]
    assert data["target_account_number"] == target_account["account_number"]

    source_check = await async_client.get(f"/accounts/account/{source_account['account_number']}")
    assert source_check.json()["balance"] == 125

    target_check = await async_client.get(f"/accounts/account/{target_account['account_number']}")
    assert target_check.json()["balance"] == 75


async def test_transfer_same_account(async_client):
    customer = await register_customer(async_client)
    account = await open_account(async_client, customer["id"])

    response = await async_client.post(
        transfer_url,
        json={
            "source_account_number": account["account_number"],
            "target_account_number": account["account_number"],
            "amount": 10,
            "description": "self",
        },
    )

    assert response.status_code == 400
    assert "same account" in response.json()["detail"]


async def test_transfer_account_not_found(async_client):
    customer = await register_customer(async_client)
    account = await open_account(async_client, customer["id"])

    response = await async_client.post(
        transfer_url,
        json={
            "source_account_number": account["account_number"],
            "target_account_number": "00000000",
            "amount": 10,
            "description": "rent",
        },
    )

    assert response.status_code == 404


async def test_transfer_insufficient_balance(async_client):
    source_customer = await register_customer(async_client, test_correct_custmor)
    target_customer = await register_customer(async_client, test_correct_custmor1)
    source_account = await open_account(async_client, source_customer["id"])
    target_account = await open_account(async_client, target_customer["id"])

    response = await async_client.post(
        transfer_url,
        json={
            "source_account_number": source_account["account_number"],
            "target_account_number": target_account["account_number"],
            "amount": 50,
            "description": "rent",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance"


# _____________________________ transfer_from_my_account _______________________

async def test_transfer_from_my_account_success(async_client):
    _source_customer, source_account, headers = await onboard_customer(
        async_client, customer=test_correct_custmor, account_type="SAVINGS"
    )
    target_customer = await register_customer(async_client, test_correct_custmor1)
    target_account = await open_account(async_client, target_customer["id"])

    await async_client.post(
        deposit_url,
        json={
            "account_number": source_account["account_number"],
            "amount": 150,
            "description": "seed",
        },
    )

    response = await async_client.post(
        transfer_from_my_account_url,
        json={
            "target_account": target_account["account_number"],
            "account_type": "SAVINGS",
            "amount": 60,
            "description": "gift",
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["target_account"] == target_account["account_number"]
    assert data["amount"] == 60


async def test_transfer_from_my_account_requires_auth(async_client):
    response = await async_client.post(
        transfer_from_my_account_url,
        json={
            "target_account": "00000000",
            "account_type": "SAVINGS",
            "amount": 10,
            "description": "gift",
        },
    )

    assert response.status_code == 401


async def test_transfer_from_my_account_no_active_source(async_client):
    _customer, _account, headers = await onboard_customer(async_client, account_type="SAVINGS")

    response = await async_client.post(
        transfer_from_my_account_url,
        json={
            "target_account": "00000000",
            "account_type": "CURRENT",
            "amount": 10,
            "description": "gift",
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert "No active CURRENT account" in response.json()["detail"]


async def test_transfer_from_my_account_target_not_found(async_client):
    _customer, _account, headers = await onboard_customer(async_client, account_type="SAVINGS")

    response = await async_client.post(
        transfer_from_my_account_url,
        json={
            "target_account": "00000000",
            "account_type": "SAVINGS",
            "amount": 10,
            "description": "gift",
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Target account not found or is not active"


async def test_transfer_from_my_account_insufficient_balance(async_client):
    _source_customer, source_account, headers = await onboard_customer(
        async_client, customer=test_correct_custmor, account_type="SAVINGS"
    )
    target_customer = await register_customer(async_client, test_correct_custmor1)
    target_account = await open_account(async_client, target_customer["id"])

    response = await async_client.post(
        transfer_from_my_account_url,
        json={
            "target_account": target_account["account_number"],
            "account_type": "SAVINGS",
            "amount": 60,
            "description": "gift",
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance"
