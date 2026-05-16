"""
Tests for JWT authentication (F4-01).

4 cases:
  1. POST /api/v1/auth/login — valid credentials → 200 + access_token
  2. POST /api/v1/auth/login — bad password → 401
  3. GET  /api/v1/auth/me    — valid token → 200 + user info
  4. GET  /api/v1/auth/me    — no token → 401
"""
import os
import sys

# Ensure the FastAPI app package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../omnidrive-web/api/app"))

from fastapi.testclient import TestClient
from main import app  # noqa: E402

client = TestClient(app)

# ── Helpers ──────────────────────────────────────────────────────────────────

_VALID_CREDENTIALS = {"email": "admin@omnidrive.io", "password": "admin123"}
_BAD_PASSWORD = {"email": "admin@omnidrive.io", "password": "wrong"}


def _get_token() -> str:
    """Log in and return the access_token."""
    resp = client.post("/api/v1/auth/login", json=_VALID_CREDENTIALS)
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# ── Tests ────────────────────────────────────────────────────────────────────


class TestLogin:
    """POST /api/v1/auth/login"""

    def test_login_ok(self):
        """Valid credentials return 200 and a JWT access_token."""
        resp = client.post("/api/v1/auth/login", json=_VALID_CREDENTIALS)
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        # Token should be a non-empty string with 3 dot-separated parts
        assert isinstance(body["access_token"], str)
        assert len(body["access_token"].split(".")) == 3

    def test_login_bad_password(self):
        """Wrong password returns 401."""
        resp = client.post("/api/v1/auth/login", json=_BAD_PASSWORD)
        assert resp.status_code == 401


class TestMe:
    """GET /api/v1/auth/me"""

    def test_me_with_valid_token(self):
        """Valid JWT returns 200 with user info."""
        token = _get_token()
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "admin@omnidrive.io"

    def test_me_without_token(self):
        """Missing Authorization header returns 401."""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401
