from .example import test_correct_custmor,test_wrong_custmor
base_url= "/customers/customers"

async def test_create_customer_success(async_client):
    response=await async_client.post(base_url,json=test_correct_custmor)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == test_correct_custmor["name"]
    assert data["email"] == test_correct_custmor["email"]
    assert data["phone"] == test_correct_custmor["phone"]

async def test_create_customer_fail(async_client):
    response=await async_client.post(base_url,json=test_wrong_custmor)
    assert response.status_code == 422
async def test_create_customer_duplicate_email(async_client):
    await async_client.post(base_url, json=test_correct_custmor)
    duplicate = {**test_correct_custmor, "phone": "0000000000"}
    response = await async_client.post(base_url, json=duplicate)
    assert response.status_code == 400
    assert "Email already used" in response.json()["detail"]
    
async def test_create_customer_duplicate_phone(async_client):
    await async_client.post(base_url, json=test_correct_custmor)
    duplicate = {**test_correct_custmor, "email": "another@example.com"}
    response = await async_client.post(base_url, json=duplicate)
    assert response.status_code == 400
    assert "Phone already used" in response.json()["detail"]

async def test_create_customer_missing_field(async_client):
    incomplete = {"name": "test", "email": "test2@example.com"} 
    response = await async_client.post(base_url, json=incomplete)
    assert response.status_code == 422
    
async def test_duplicate_email_error_reveals_existing_id(async_client):
    create_response = await async_client.post(base_url, json=test_correct_custmor)
    existing_id = create_response.json()["id"]

    duplicate = {**test_correct_custmor, "phone": "0000000000"}
    response = await async_client.post(base_url, json=duplicate)
    assert existing_id in response.json()["detail"]
