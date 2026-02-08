from fastapi import Header

# If the param is func, it will be mandatory, so we set default to None to make it optional until authentication is implemented
def optional_user(authorization: str | None = Header(default=None)):
    return None