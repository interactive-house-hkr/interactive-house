from pydantic import BaseModel, EmailStr, Field

"""
Pydantic models for authentication and user data.

- Defines request schemas for registration, login, and refresh tokens
- Defines response schemas for authentication responses
- Validates user-related input and output data
"""

class RegisterRequest(BaseModel):
  username: str = Field(..., min_length=3, max_length=50)
  email: EmailStr
  password: str = Field(..., min_length=6)

class RegisterResponse(BaseModel):
  status: str
  user_id: str
  access_token: str
  refresh_token: str

class LoginRequest(BaseModel):
  username: str
  password: str

class LoginResponse(BaseModel):
  status: str
  user_id: str
  access_token: str
  refresh_token: str

class RefreshTokenRequest(BaseModel):
  refresh_token: str

class UserResponse(BaseModel):
  id: str
  username: str
  email: EmailStr
