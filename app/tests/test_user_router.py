import uuid

from .example import (
    test_correct_custmor,
    DEFAULT_PASSWORD,
    register_customer,
    register_login,
    login,
)

create_url = "/user/create"
get_url = "/user/get/{email}"
login_url = "/user/login"
logout_url = "/user/logout"


async def test_create_user_success(async_client):
    customer = await register_customer(async_client)

    response = await async_client.post(
        create_url,
        json={"customer_id": customer["id"], "password": DEFAULT_PASSWORD},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer["id"]
    assert "id" in data


async def test_create_user_customer_not_found(async_client):
    response = await async_client.post(
        create_url,
        json={"customer_id": str(uuid.uuid4()), "password": DEFAULT_PASSWORD},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


async def test_create_user_missing_field(async_client):
    response = await async_client.post(create_url, json={"password": DEFAULT_PASSWORD})

    assert response.status_code == 422


async def test_get_user_success(async_client):
    customer = await register_customer(async_client)
    await register_login(async_client, customer["id"])

    response = await async_client.get(get_url.format(email=customer["email"]))

    assert response.status_code == 200
    assert response.json()["customer_id"] == customer["id"]


async def test_get_user_not_found(async_client):
    response = await async_client.get(get_url.format(email="nobody@example.com"))

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


async def test_login_success(async_client):
    customer = await register_customer(async_client)
    await register_login(async_client, customer["id"])

    response = await async_client.post(
        login_url,
        data={"username": customer["email"], "password": DEFAULT_PASSWORD},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "Bearer"
    assert data["access_token"]


async def test_login_wrong_password(async_client):
    customer = await register_customer(async_client)
    await register_login(async_client, customer["id"])

    response = await async_client.post(
        login_url,
        data={"username": customer["email"], "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_login_unknown_user(async_client):
    response = await async_client.post(
        login_url,
        data={"username": "nobody@example.com", "password": DEFAULT_PASSWORD},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


async def test_logout_success(async_client):
    customer = await register_customer(async_client)
    await register_login(async_client, customer["id"])
    token = await login(async_client, customer["email"])

    response = await async_client.post(
        logout_url,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


async def test_logout_requires_auth(async_client):
    response = await async_client.post(logout_url)

    assert response.status_code == 401


async def test_logout_token_cannot_be_reused(async_client):
    customer = await register_customer(async_client)
    await register_login(async_client, customer["id"])
    token = await login(async_client, customer["email"])
    headers = {"Authorization": f"Bearer {token}"}

    first_logout = await async_client.post(logout_url, headers=headers)
    assert first_logout.status_code == 200

    second_logout = await async_client.post(logout_url, headers=headers)
    assert second_logout.status_code == 401
    assert second_logout.json()["detail"] == "Token is blacklisted"
