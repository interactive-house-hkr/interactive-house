from src.utils.security import (
  hash_password,
  create_access_token,
  create_refresh_token,
  verify_password
  )
from src.schemas.auth_schema import (
  RegisterRequest,
  LoginRequest
)
from firebase_admin import db
from fastapi import HTTPException
import uuid

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
  # Databse references
  users_ref = db.reference("users")# -> All users
  usernames_ref = db.reference("usernames")# -> All usernames for lookup

  # Username is normalized 
  username = user.username.lower()

  # Does the already exist? -> 400 ERROR
  if usernames_ref.child(username).get():
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
  users_ref.child(user_id).set(user_data)
  usernames_ref.child(username).set(user_id)
  
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
  # Database references
  users_ref = db.reference("users")# -> All users
  usernames_ref = db.reference("usernames")# -> All usernames for lookup

  # Normalize username and get user_id  
  username = user.username.lower()
  user_id = usernames_ref.child(username).get()

  # Wrong username? -> 401 ERROR
  if not user_id:
    unauthorized_error()

  # User from database
  db_user = users_ref.child(user_id).get()
  
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