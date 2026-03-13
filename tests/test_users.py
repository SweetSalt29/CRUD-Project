import sys
 
sys.path.append("/home/aryan-tamhane/Desktop/CRUD Project")
 
from fastapi.testclient import TestClient
from app.main import app
from app.auth import hash_password, verify_password
 
client = TestClient(app)
 
 
# NORMAL TEST CASE
 
def test_register_user():
    response = client.post(
        "/register",
        json={
            "username": "Aaryan",
            "email": "aaryan@example.com",
            "password": "Password1"
        }
    )
 
    print("\nRegister User Test")
    print("Status Code:", response.status_code)
 
    if response.status_code == 200:
        print("Message: User registered successfully")
    else:
        print("Message: Registration failed")
 
    print("Response:", response.json())
 
    assert response.status_code == 200
 
 
def test_login_user():
    response = client.post(
        "/login",
        json={
            "username": "Aaryan",
            "password": "Password1"
        }
    )
 
    print("\nLogin User Test")
    print("Status Code:", response.status_code)
 
    if response.status_code == 200:
        print("Message: Login successful")
    else:
        print("Message: Login failed")
 
    print("Response:", response.json())
 
    assert response.status_code == 200
 
 
 
# EDGE TEST CASE
 
def test_password_min_length():
    response = client.post(
        "/register",
        json={
            "username": "riya",
            "email": "riya@gmail.com",
            "password": "abcD5"
        }
    )
 
    print("\nEdge Case: Minimum Password Length")   #min_length=4
    print("Status Code:", response.status_code)
 
    if response.status_code == 200:
        print("Message: Password accepted at minimum boundary")
    else:
        print("Message: Password rejected")
 
    print("Response:", response.json())
 
    assert response.status_code == 200
 
 
def test_long_username():
    response = client.post(
        "/register",
        json={
            "username": "a"*50,
            "email": "longuser@gmail.com",
            "password": "Password1"
        }
    )
 
    print("\nEdge Case: Long Username")
    print("Status Code:", response.status_code)
 
    if response.status_code == 200:
        print("Message: Username accepted at maximum length")
    else:
        print("Message: Username rejected")
 
    print("Response:", response.json())
 
    assert response.status_code == 200
 
 
# NEGATIVE TEST CASES
 
def test_invalid_email():
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "invalid-email",
            "password": "Password1"
        }
    )
 
    print("\nNegative Test: Invalid Email")
    print("Status Code:", response.status_code)
    print("Message: Invalid email format")
    print("Response:", response.json())
 
    assert response.status_code == 422
 
 
def test_invalid_password():
    response = client.post(
        "/register",
        json={
            "username": "testuser2",
            "email": "testuser2@gmail.com",
            "password": "abc"
        }
    )
 
    print("\nNegative Test: Invalid Password")
    print("Status Code:", response.status_code)
    print("Message: Invalid password (does not meet requirements)")
    print("Response:", response.json())
 
    assert response.status_code in [400, 422]
 
 
# UNIT TEST CASE
 
def test_hash_password():
    password = "Password1"
    hashed = hash_password(password)
 
    print("\nUnit Test: Hash Password")
    print("Original Password:", password)
    print("Hashed Password:", hashed)
 
    assert hashed != password
 
 
def test_verify_password():
    password = "Password1"
    hashed = hash_password(password)
 
    result = verify_password(password, hashed)
 
    print("\nUnit Test: Verify Password")
    print("Verification Result:", result)
 
    assert result == True