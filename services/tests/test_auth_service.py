import pytest
from services.src.services import auth_service
from services.src.schemas.auth_schema import RegisterRequest, LoginRequest


"""
Fixtures to make mock user object data:

- User login
- User register

returns dictionary of user data
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
Unit tests for user registration.

-
-
-
-
-
"""

def test_successful_registration(monkeypatch, user_register):
  monkeypatch.setattr(auth_service.user_store, "get_user_id_by_username", lambda username: None)
  monkeypatch.setattr(auth_service, "hash_password", lambda password: "hashed")
  monkeypatch.setattr(auth_service.user_store, "save_user",lambda user_id, user_data: None)
  monkeypatch.setattr(auth_service.user_store, "save_username", lambda username, user_id: None)
  monkeypatch.setattr(auth_service, "create_access_token", lambda user_id: "access-token")
  monkeypatch.setattr(auth_service, "create_refresh_token", lambda user_id: "refresh-token")
  
  result = auth_service.register(user_register)
  assert result["status"] == "success"
  

def test_registration_fails_if_username_exists():
  pass

def test_registration_saves_user():
  pass

def test_registration_saves_username_mapping():
  pass

def test_registration_returns_success_response():
  pass


"""
Unit tests for user login.

-
-
-
-
-
"""

def test_successful_login():
  pass

def test_login_fails_if_username_does_not_exist():
  pass

def test_login_fails_if_user_data_is_missing():
  pass

def test_login_fails_if_password_is_incorrect():
  pass

def test_login_returns_success_response():
  pass



