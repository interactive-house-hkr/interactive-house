from fastapi import APIRouter
from services.src.controllers import auth_controller
from services.src.schemas.auth_schema import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)

"""
Routes for user registration and login.

- Registers new users
- Authenticates existing users

Returns authentication responses from the controller layer.
"""

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register")
def register(user: RegisterRequest) -> RegisterResponse:
    return auth_controller.register(user)

@router.post("/login")
def login(user: LoginRequest) -> LoginResponse:
    return auth_controller.login(user)

