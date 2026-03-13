import pytest
import time
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth import hash_password, verify_password

# This makes the transport reusable for all tests in this file
transport = ASGITransport(app=app)

# --- UNIT TESTS ---

def test_hash_password():
    password = "Password1"
    hashed = hash_password(password)
    print(f"\nUnit Test Hash: {hashed}")
    assert hashed != password

def test_verify_password():
    password = "Password1"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True

# --- API TESTS (MUST BE ASYNC) ---

@pytest.mark.asyncio
async def test_register_user_success():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_email = f"Aaryan_{int(time.time())}@gmail.com"
        response = await ac.post("/auth/register", json={
            "email": unique_email,
            "password": "Password1",
            "role": "student"
        })
        print(f"\nRegister Status: {response.status_code}")
        assert response.status_code == 200
        assert response.json()["email"] == unique_email

@pytest.mark.asyncio
async def test_invalid_email_format():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={
            "email": "not-an-email",
            "password": "Password1"
        })
        print(f"\nNegative Test (Email) Status: {response.status_code}")
        # Pydantic returns 422 for validation errors
        assert response.status_code == 422 

@pytest.mark.asyncio
async def test_password_too_short():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={
            "email": "short@gmail.com",
            "password": "123" # Too short based on our Field(min_length=4)
        })
        assert response.status_code == 422