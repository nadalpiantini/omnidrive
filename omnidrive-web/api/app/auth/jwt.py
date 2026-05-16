"""
JWT token creation and validation for OmniDrive API.

Uses python-jose with HS256. Secret comes from OMNIDRIVE_JWT_SECRET
environment variable (falls back to a dev value with a WARNING).
"""
import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

_ALGORITHM = "HS256"
_DEV_SECRET = "change-me-in-prod"


def _get_secret() -> str:
    """Return the JWT signing secret.

    Reads ``OMNIDRIVE_JWT_SECRET`` from the environment.
    In development mode (ENVIRONMENT=development or NODE_ENV=development)
    a hard-coded dev fallback is used with a loud warning.
    In any other environment the function raises RuntimeError to prevent
    silent deployment with an insecure secret.
    """
    secret = os.getenv("OMNIDRIVE_JWT_SECRET", "").strip()
    if secret:
        return secret

    env = os.getenv("ENVIRONMENT", os.getenv("NODE_ENV", "")).strip().lower()
    if env == "development":
        logger.warning(
            "OMNIDRIVE_JWT_SECRET not set — using insecure dev fallback. "
            "Set the env var before deploying to production!"
        )
        return _DEV_SECRET

    raise RuntimeError(
        "OMNIDRIVE_JWT_SECRET is not set and ENVIRONMENT is not 'development'. "
        "Set the OMNIDRIVE_JWT_SECRET environment variable to start the API."
    )


def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    """Create a signed JWT with *subject* as the ``sub`` claim.

    Parameters
    ----------
    subject:
        Unique identifier for the user (e.g. email).
    expires_minutes:
        Token lifetime in minutes.  Defaults to 60.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, _get_secret(), algorithm=_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT.

    Returns the payload dict on success.

    Raises
    ------
    HTTPException (401)
        If the token is expired, malformed, or has an invalid signature.
    """
    try:
        payload: dict = jwt.decode(token, _get_secret(), algorithms=[_ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
