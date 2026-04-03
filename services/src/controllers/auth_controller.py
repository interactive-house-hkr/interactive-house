from services.src.schemas.auth_schema import LoginRequest, RegisterRequest
from services.src.services import auth_service

"""
Controller for auth routes:

- Handles user registration through the service layer
- Handles user login through the service layer

Returns authentication responses from the auth service
"""

def register(user: RegisterRequest):
    return auth_service.register(user)

def login(user: LoginRequest):
    return auth_service.login(user)
