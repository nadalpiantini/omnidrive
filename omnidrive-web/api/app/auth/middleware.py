"""
Authentication dependency for FastAPI route protection.

Usage::

    from auth.middleware import get_current_user

    @router.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        ...
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from auth.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency that extracts and validates the JWT from the
    ``Authorization: Bearer <token>`` header.

    Returns the decoded payload (contains at least ``sub``).

    Raises HTTPException 401 when the token is missing or invalid.
    """
    return decode_token(token)
