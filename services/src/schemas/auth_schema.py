from pydantic import BaseModel, EmailStr, Field

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

class TokenResponse(BaseModel):
  status: str
  user_id: str
  token: str

class RefreshTokenRequest(BaseModel):
  refresh_token: str

class UserResponse(BaseModel):
  id: str
  username: str
  email: EmailStr