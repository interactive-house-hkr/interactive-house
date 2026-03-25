from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from jwt import InvalidTokenError
from typing import Any, Optional
from config import Settings
import jwt
import bcrypt
import secrets

settings = Settings()

"""
The password is encoded to bytes as bcrypt uses bytes.
Salt is generated and the password is hashed using
that salt. The hash is decoded to a string so it
can be stored in  the DB.
"""

def hash_password(password: str) -> str:
  arr_bytes = password.encode("utf-8")
  salt = bcrypt.gensalt()
  pass_hash = bcrypt.hashpw(arr_bytes, salt)

  return pass_hash.decode("utf-8")

"""
Takes provided_password from user and checks using .checkpw().
to see if it matches password stored in DB.
"""

def verify_password(provided_password: str, stored_password: str) -> bool:
  provided_password = provided_password.encode("utf-8")
  stored_password = stored_password.encode("utf-8")
  
  verified = bcrypt.checkpw(provided_password, stored_password)

  return verified

"""
Takes a dictionary in json format (str, any) and optional expiration time.
The expiration timeframe is decided if a time has been provided in the arguments
otherwise it's take from the settings. The copied dictionary is the updated with neceary
data and encoded as a JWT and signs it.
"""

def create_access_token(user_id: str, extra_claims: Optional[dict[str, Any]] = None, expires_delta: timedelta | None = None) -> str:

  now = datetime.now(timezone.utc)
  expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

  payload ={
    "exp": expire,
    "iat": now,
    "type": "access",
    "jti": secrets.token_urlsafe(16),
    "sub": user_id
  }

  # If extra claims such as "role": "admin" are added
  # the jwt payload will be updated
  if extra_claims:
    payload.update(extra_claims)

  return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

"""
Same as create_access_token() with minor changes.
"""

def create_refresh_token(user_id: str, extra_claims: Optional[dict[str, Any]] = None, expires_delta: timedelta | None = None) -> str:

  now = datetime.now(timezone.utc)
  expire = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

  payload ={
    "exp": expire,
    "iat": now,
    "type": "refresh",
    "jti": secrets.token_urlsafe(16),
    "sub": user_id
  }


  if extra_claims:
    payload.update(extra_claims)

  return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

"""
Decodes the token to check if the token is valid else an error is raised.
"""

def decode_token(token: str) -> dict[str, Any]: 
  try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload
  except InvalidTokenError as e:
    raise ValueError(f"Invalid token {e}")

"""
Functions to verify the token type. If the tokens to not match
a 401 error is raised.
"""    

def verify_access_token(payload: dict[str, Any]) -> None:
  if payload.get("type") != "access":
    raise HTTPException(status_code=401, detail="Unauthorized")

def verify_refresh_token(payload: dict[str, Any]) -> None:
  if payload.get("type") != "refresh":
    raise HTTPException(status_code=401, detail="Unauthorized")