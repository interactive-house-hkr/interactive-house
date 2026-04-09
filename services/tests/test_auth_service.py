import pytest
from services.src.services import auth_service
from services.src.schemas.auth_schema import RegisterRequest, LoginRequest
from fastapi import HTTPException

"""
------------------------------------------
| Fixtures to make mock user object data |
------------------------------------------
- User login
- User register

returns objects of user data
"""

@pytest.fixture
def user_login():
  return LoginRequest(
    username= "testUser",
    password= "123456"
  )
  
@pytest.fixture
def user_register():
  return RegisterRequest(
    username= "testUser",
    email= "test@example.com",
    password= "123456"
  )

"""
------------------------------------
| Unit tests for user registration |
------------------------------------
- Tests successful registration
- Tests failed registration if user exists
- Tests if registrations saves user
- Tests username mapping 
"""

def test_successful_registration(monkeypatch, user_register):

  # Mock external dependencies used in register():
  # username lookup, password hashing, database writes, and token creation.

  monkeypatch.setattr(auth_service.user_store, "get_user_id_by_username", lambda username: None)
  monkeypatch.setattr(auth_service, "hash_password", lambda password: "hashed")
  monkeypatch.setattr(auth_service.user_store, "save_user",lambda user_id, user_data: None)
  monkeypatch.setattr(auth_service.user_store, "save_username", lambda username, user_id: None)
  monkeypatch.setattr(auth_service, "create_access_token", lambda user_id: "access-token")
  monkeypatch.setattr(auth_service, "create_refresh_token", lambda user_id: "refresh-token")
  
  result = auth_service.register(user_register)
  assert result["status"] == "success"
  

def test_registration_fails_if_username_exists(monkeypatch, user_register):

  # Mock the username lookup to simulate that the user already exists.
  # Registration stops before any other function is called.

  monkeypatch.setattr(auth_service.user_store, "get_user_id_by_username", lambda username: "existing-user-id")
  monkeypatch.setattr(auth_service, "hash_password", lambda password: "hashed")
  monkeypatch.setattr(auth_service.user_store, "save_user",lambda user_id, user_data: None)
  monkeypatch.setattr(auth_service.user_store, "save_username", lambda username, user_id: None)
  monkeypatch.setattr(auth_service, "create_access_token", lambda user_id: "access-token")
  monkeypatch.setattr(auth_service, "create_refresh_token", lambda user_id: "refresh-token")

  with pytest.raises(HTTPException) as exc_info:
    auth_service.register(user_register)

  assert exc_info.value.status_code == 400
  assert exc_info.value.detail == "User already exists"


def test_registration_saves_user(monkeypatch, user_register):
  saved = {}

  def mock_saved_user(user_id, user_data):
    saved["user_id"] = user_id
    saved["user_data"] = user_data

  # Mock external dependencies and capture the arguments passed to save_user()
  # so the test can verify what registration tries to store.

  monkeypatch.setattr(auth_service.user_store, "get_user_id_by_username", lambda username: None)
  monkeypatch.setattr(auth_service.user_store, "save_user", mock_saved_user)
  monkeypatch.setattr(auth_service.user_store, "save_username", lambda username, user_id: None)
  monkeypatch.setattr(auth_service, "hash_password", lambda password: "hashed")
  monkeypatch.setattr(auth_service, "create_access_token", lambda user_id: "access-token")
  monkeypatch.setattr(auth_service, "create_refresh_token", lambda user_id: "refresh-token")
  
  auth_service.register(user_register)

  assert "user_id" in saved
  assert saved["user_data"]["username"] == "testuser"
  assert saved["user_data"]["email"] == "test@example.com"
  assert saved["user_data"]["password_hash"] == "hashed"

def test_registration_saves_username_mapping(monkeypatch, user_register):
  saved = {}

  def mock_save_username(username, user_id):
    saved["username"] = username
    saved["user_id"] = user_id

  # Mock external dependencies and capture the arguments passed to save_username()
  # so the test can verify that the username mapping is stored correctly.

  monkeypatch.setattr(auth_service.user_store, "get_user_id_by_username", lambda username: None)
  monkeypatch.setattr(auth_service.user_store, "save_user", lambda user_id, user_data: None)
  monkeypatch.setattr(auth_service.user_store, "save_username", mock_save_username)
  monkeypatch.setattr(auth_service, "hash_password", lambda password: "hashed")
  monkeypatch.setattr(auth_service, "create_access_token", lambda user_id: "access-token")
  monkeypatch.setattr(auth_service, "create_refresh_token", lambda user_id: "refresh-token")
  
  auth_service.register(user_register)

  assert "username" in saved
  assert "user_id" in saved
  assert saved["username"] == "testuser"

"""
-----------------------------
| Unit tests for user login |
-----------------------------
- Tests successful login.
- Tests if login fails username does not exists.
- Tests login fails if user data is missing.
- 
"""

def test_successful_login(monkeypatch, user_login):

  # Mock external dependencies so the test only verifies
  # the login logic in auth_service, not database access or real token generation.

  monkeypatch.setattr(auth_service.user_store, "get_user_id_by_username", lambda username: "existing-user-id")
  monkeypatch.setattr(auth_service.user_store, "get_user", lambda user_id: {"password_hash": "stored-hash"})
  monkeypatch.setattr(auth_service, "verify_password", lambda provided_password, stored_password: True)
  monkeypatch.setattr(auth_service, "create_access_token", lambda user_id: "access-token")
  monkeypatch.setattr(auth_service, "create_refresh_token", lambda user_id: "refresh-token")

  result = auth_service.login(user_login)
  assert result["status"] == "success"


def test_login_fails_if_username_does_not_exist(monkeypatch, user_login):

  # Mock the username lookup to simulate a missing user.
  # Other dependencies are not reached because login fails immediately.

  monkeypatch.setattr(auth_service.user_store, "get_user_id_by_username", lambda username: None)
  monkeypatch.setattr(auth_service.user_store, "get_user", lambda user_id: None)
  monkeypatch.setattr(auth_service, "verify_password", lambda provided_password, stored_password: False)
  monkeypatch.setattr(auth_service, "create_access_token", lambda user_id: None)
  monkeypatch.setattr(auth_service, "create_refresh_token", lambda user_id: None)

  with pytest.raises(HTTPException) as exc_info:
    auth_service.login(user_login)

  assert exc_info.value.status_code == 401
  assert exc_info.value.detail == "Invalid credentials"

def test_login_fails_if_user_data_is_missing(monkeypatch, user_login):

  # Mock the user lookup to simulate that the username exists
  # but no user data is found in the database.

  monkeypatch.setattr(auth_service.user_store, "get_user_id_by_username", lambda username: "existing-user-id")
  monkeypatch.setattr(auth_service.user_store, "get_user", lambda user_id: None)

  with pytest.raises(HTTPException) as exc_info:
    auth_service.login(user_login)
  
  assert exc_info.value.status_code == 401
  assert exc_info.value.detail == "Invalid credentials"

def test_login_fails_if_password_is_incorrect(monkeypatch, user_login):

  # Mock the user lookup and password check to simulate
  # a login attempt with an incorrect password.

  monkeypatch.setattr(auth_service.user_store, "get_user_id_by_username", lambda username: "existing-user-id")
  monkeypatch.setattr(auth_service.user_store, "get_user", lambda user_id: {"password_hash": "stored-hash"})
  monkeypatch.setattr(auth_service, "verify_password", lambda provided_password, stored_password: False)

  with pytest.raises(HTTPException) as exc_info:
    auth_service.login(user_login)
  
  assert exc_info.value.status_code == 401
  assert exc_info.value.detail == "Invalid credentials"