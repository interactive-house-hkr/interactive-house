import pytest
from services.src.dependencies import auth
from fastapi import HTTPException
from jwt import InvalidTokenError

"""
------------------------------------------
| Unit tests for current user dependency |
------------------------------------------
- Tests valid bearer token handling
- Tests 401 responses for invalid or malformed authorization headers
- Tests 401 responses for token decode, verification, and payload errors
"""

def test_current_user_returns_sub_for_valid_bearer_token(monkeypatch):

  # Mock token decoding and access-token verification
  # so the test only checks that current_user returns the user ID for a valid bearer token.

  monkeypatch.setattr(auth, "decode_token", lambda token: {"sub": "user-123", "type": "access"})
  monkeypatch.setattr(auth, "verify_access_token", lambda payload: None)

  result = auth.current_user("Bearer valid-token")
  assert result == "user-123"

def test_current_user_raises_401_for_invalid_auth_schema():
  
  # Pass an authorization header with an invalid scheme
  # to verify that current_user raises a 401 error.

  with pytest.raises(HTTPException) as exc_info:
    auth.current_user("No Bearer")

  assert exc_info.value.status_code == 401
  assert exc_info.value.detail == "Invalid auth scheme"

def test_current_user_raises_401_when_authorization_header_is_malformed():

  # Pass a malformed authorization header
  # to verify that current_user raises a 401 error.

  with pytest.raises(HTTPException) as exc_info: 
    auth.current_user("Malformed_token")

  assert exc_info.value.status_code == 401
  assert exc_info.value.detail == "Invalid or missing token"


def test_current_user_raises_401_when_decode_token_fails(monkeypatch):

  # Mock decode_token to simulate an invalid token
  # and verify that current_user raises a 401 error.

  def mock_decode_token(token):
    raise InvalidTokenError("Invalid token")
  
  monkeypatch.setattr(auth, "decode_token", mock_decode_token)
  
  with pytest.raises(HTTPException) as exc_info:
    auth.current_user("Bearer valid-token")

  assert exc_info.value.status_code == 401
  assert exc_info.value.detail == "Invalid or missing token"


def test_current_user_raises_401_when_verify_access_token_fails(monkeypatch):
  
  # Mock access-token verification to simulate a token validation failure
  # and verify that current_user raises a 401 error.

  def mock_verify_access_token(token):
    raise InvalidTokenError("Invalid token")
  
  monkeypatch.setattr(auth, "decode_token", lambda token: {"sub": "user-123", "type": "access"})
  monkeypatch.setattr(auth, "verify_access_token", mock_verify_access_token)
  
  with pytest.raises(HTTPException) as exc_info:
    auth.current_user("Bearer valid-token")

  assert exc_info.value.status_code == 401
  assert exc_info.value.detail == "Invalid or missing token"

def test_current_user_raises_401_when_payload_missing_sub(monkeypatch):

  # Mock a decoded payload without a user ID (sub)
  # to verify that current_user raises a 401 error.

  monkeypatch.setattr(auth, "decode_token", lambda token: {"type": "access"})
  monkeypatch.setattr(auth, "verify_access_token", lambda payload: None)

  with pytest.raises(HTTPException) as exc_info: 
    auth.current_user("Bearer valid-token")
  
  assert exc_info.value.status_code == 401
  assert exc_info.value.detail == "Invalid or missing token"
