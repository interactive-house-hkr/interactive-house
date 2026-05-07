import pytest
from services.src.controllers import auth_controller
from fastapi.testclient import TestClient
from services.src.main import app
from fastapi import HTTPException

@pytest.fixture
def client():
    return TestClient(app)

"""
---------------------------
| Tests for user register |
---------------------------
- Valid registration returns a success response
- Invalid username, email, or password returns validation errors
- Missing required fields returns validation errors
- Existing user returns a 400 error
"""

def test_register_returns_success_response(client, monkeypatch):
  
  # Checks that valid registration returns 200.
  # Checks that the response contains success data.
  
  monkeypatch.setattr(auth_controller, "register", lambda user: {
    "status": "success",
    "user_id": "123",
    "access_token": "token",
    "refresh_token": "refresh"
  })
  response = client.post("/api/v1/auth/register", json ={
    "username": "testUser",
    "email": "test@example.com",
    "password": "123456"
  })
  
  assert response.status_code == 200
  assert response.json()["status"] == "success"

def test_register_rejects_short_username(client):
  
  # Checks that a too short username is rejected.
  # Checks that the route returns a validation error.
  
  response = client.post("/api/v1/auth/register", json ={
    "username": "t",
    "email": "test@example.com",
    "password": "123456"
  })

  body = response.json()

  assert response.status_code == 422
  assert "detail" in body
  assert body["detail"][0]["loc"] == ["body", "username"]
  
  
def test_register_rejects_invalid_email(client):
  
  # Checks that an invalid email is rejected.
  # Checks that the route returns a validation error.
  
  response = client.post("/api/v1/auth/register", json ={
    "username": "testUser",
    "email": "@",
    "password": "123456"
  })
  
  body = response.json()
  
  assert response.status_code == 422
  assert "detail" in body
  assert body["detail"][0]["loc"] == ["body", "email"]


def test_register_rejects_short_password(client):
  
  # Checks that a too short password is rejected.
  # Checks that the route returns a validation error.
  
  response = client.post("/api/v1/auth/register", json ={
    "username": "testUser",
    "email": "test@example.com",
    "password": "1"
  })
  
  body = response.json()
  
  assert response.status_code == 422
  assert "detail" in body
  assert body["detail"][0]["loc"] == ["body", "password"]

def test_register_rejects_missing_username(client):
  
  # Checks that missing username is rejected.
  # Checks that the route returns a validation error. 
  
  response = client.post("/api/v1/auth/register", json ={
    "email": "test@example.com",
    "password": "123456"
  })

  body = response.json()
  
  assert response.status_code == 422
  assert "detail" in body
  assert body["detail"][0]["loc"] == ["body", "username"]

def test_register_rejects_missing_email(client):
   
  # Checks that missing email is rejected.
  # Checks that the route returns a validation error.
  
  response = client.post("/api/v1/auth/register", json ={
    "username": "testUser",
    "password": "123456"
  })
  
  body = response.json()
  
  assert response.status_code == 422
  assert "detail" in body
  assert body["detail"][0]["loc"] == ["body", "email"]
  

def test_register_rejects_missing_password(client):
  
  # Checks that missing password is rejected.
  # Checks that the route returns a validation error.
  
  response = client.post("/api/v1/auth/register", json ={
    "username": "testUser",
    "email": "test@example.com",
  })
  
  body = response.json()
  
  assert response.status_code == 422
  assert "detail" in body
  assert body["detail"][0]["loc"] == ["body", "password"]
  
def test_register_returns_400_when_user_already_exists(client, monkeypatch):

  # Checks that an existing user is rejected.
  # Checks that the route returns a 400 error.

  def user_already_exists(user):
    raise HTTPException(status_code=400, detail="User already exists")
    
  monkeypatch.setattr(auth_controller, "register", user_already_exists)
  response = client.post("/api/v1/auth/register", json ={
    "username": "testUser",
    "email": "test@example.com",
    "password": "123456"
  })
  
  assert response.status_code == 400
  assert response.json()["detail"] == "User already exists"
  
"""
------------------------------
| Tests for user login route |
------------------------------
- Missing username returns validation error
- Missing password returns validation error
- Invalid credentials return a 401 error
"""

def test_login_rejects_missing_username(client):
  
  # Checks that missing username is rejected.
  # Checks that the route returns a validation error.
  
  response = client.post("/api/v1/auth/login", json ={
    "password": "123456"
  })
  
  body = response.json()
  
  assert response.status_code == 422
  assert "detail" in body
  assert any(error["loc"] == ["body", "username"] for error in body["detail"])
  

def test_login_rejects_missing_password(client):
  
  # Checks that missing password is rejected.
  # Checks that the route returns a validation error.
  
  response = client.post("/api/v1/auth/login", json ={
    "username": "testUser",
  })
  
  body = response.json()
  
  assert response.status_code == 422
  assert "detail" in body
  assert any(error["loc"] == ["body", "password"] for error in body["detail"])

def test_login_returns_401_for_invalid_credentials(client, monkeypatch):
  
  # Checks that invalid credentials are rejected.
  # Checks that the route returns a 401 error.
 
  def invalid_credentials(user):
    raise HTTPException(status_code=401, detail="Invalid credentials")
    
  monkeypatch.setattr(auth_controller, "login", invalid_credentials)
  response = client.post("/api/v1/auth/login", json ={
    "username": "testUser",
    "password": "123456"
  })
  
  assert response.status_code == 401
  assert response.json()["detail"] == "Invalid credentials"