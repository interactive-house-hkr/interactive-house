from fastapi import Header, HTTPException
from services.src.utils.security import decode_token, verify_access_token
from jwt import InvalidTokenError


# If the param is func, it will be mandatory, so we set default to None to make it optional until authentication is implemented
def optional_user(authorization: str | None = Header(default=None)):
    return None

"""
Accessing current user:

- Expects and validates the current user from Authorization header.
- Decodes and verifies the token.
- Raises 401 if the token is missing, invalid or incorrectly formatted.

Returns the user ID (sub).
"""

def current_user(authorization: str = Header(...))-> str:
    try:
        # scheme = "Bearer ", token = "abc123"
        scheme, token = authorization.split()

        # Checks auth-type
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        
        payload = decode_token(token) # Token is decoded
        verify_access_token(payload) # Is the token valid?

        return payload["sub"]
    except HTTPException:
        raise
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    except (ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid or missing token")