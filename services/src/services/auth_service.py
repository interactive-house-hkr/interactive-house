from services.src.utils.security import (
  hash_password,
  create_access_token,
  create_refresh_token,
  verify_password
  )
from services.src.schemas.auth_schema import (
  RegisterRequest,
  LoginRequest
)
from fastapi import HTTPException
import uuid
from services.src.firebase import user_store

"""
Registers a new user:

-Normalizes username
-Checks if user already exists
-Hashes password
-Stores user data in Database
-Generates access and refresh tokens

Returns a success response with tokens.
"""

def register(user: RegisterRequest):

  # Username is normalized 
  username = user.username.lower()

  # Does the already exist? -> 400 ERROR
  if user_store.get_user_id_by_username(username):
    raise HTTPException(status_code=400, detail="User already exists")

  
  # Hash password and create a unique user_id
  password_hash = hash_password(user.password)
  user_id = str(uuid.uuid4())

  # Creates user data  
  user_data = {
    "user_id": user_id,
    "username": username,
    "email": user.email,
    "password_hash": password_hash
  }
   
  # Saves user and username
  user_store.save_user(user_id, user_data)
  user_store.save_username(username, user_id)

  
  # Creates tokens
  access_token = create_access_token(user_id)
  refresh_token = create_refresh_token(user_id)

  # Return response
  return {
    "status": "success",
    "user_id": user_id,
    "access_token": access_token,
    "refresh_token": refresh_token
  }

"""
User Login:

-Normalized username
-Checks username and if user exists
-Checks password
-Generates access and refresh tokens

Returns a success response with tokens.
"""

def login(user: LoginRequest):

  # Normalize username and get user_id  
  username = user.username.lower()
  user_id = user_store.get_user_id_by_username(username)


  # Wrong username? -> 401 ERROR
  if not user_id:
    unauthorized_error()

  # User from database
  db_user = user_store.get_user(user_id)
  
  # Does the user exist? -> 401 ERROR
  if not db_user:
    unauthorized_error()
  
  # Wrong passsword? -> 401 ERROR
  if not verify_password(user.password, db_user.get("password_hash")):
    unauthorized_error()
  
  # Creates tokens
  access_token = create_access_token(user_id)
  refresh_token = create_refresh_token(user_id)

  # Return response  
  return {
    "status": "success",
    "user_id": user_id,
    "access_token": access_token,
    "refresh_token": refresh_token
  }

"""
Frequently used error (401 Unauthorized) in this file.
Made it to function for better readability and reuseability
"""
def unauthorized_error():
  raise HTTPException(status_code=401, detail="Invalid credentials")

