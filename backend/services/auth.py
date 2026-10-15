"""
NutriSphere 3D - Authentication & Identity Management
Replaces client-trusted X-User-Id headers with server-validated cryptographic session tokens.
Includes:
- PBKDF2 user password authentication
- Cryptographic session token generation & verification
- Isolated development-only demo token mechanism that is strictly disabled in production
- get_current_user dependency for route authorization
"""

import os
import secrets
import time
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.database import get_db, verify_password

# In-memory active session tokens store: {token: {"user_id": str, "expires_at": float, "is_demo": bool}}
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

# Isolated dev/demo token - strictly disabled if NUTRISPHERE_ENV == "production"
DEV_DEMO_TOKEN = "nutrisphere_dev_demo_token_secure_2026"
IS_PRODUCTION = os.environ.get("NUTRISPHERE_ENV", "development").lower() == "production"

security_bearer = HTTPBearer(auto_error=False)


def create_session_token(user_id: str, is_demo: bool = False, duration_seconds: int = 86400) -> str:
    """Generate a cryptographically secure random session token."""
    token = secrets.token_hex(32)
    ACTIVE_SESSIONS[token] = {
        "user_id": user_id,
        "expires_at": time.time() + duration_seconds,
        "is_demo": is_demo
    }
    return token


def authenticate_user_credentials(username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
    """Validate username or email and password against SQLite users table."""
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, username, email, password_hash, salt, role, is_active FROM users WHERE username = ? OR email = ?;",
            (username_or_email, username_or_email)
        ).fetchone()

        if not user or not user["is_active"]:
            return None

        if verify_password(password, user["salt"], user["password_hash"]):
            return dict(user)
    return None


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Dict[str, Any]:
    """
    FastAPI dependency that enforces server-validated authentication.
    Strictly verifies Bearer token against active server sessions.
    Replaces client-trusted X-User-Id headers.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing Bearer token in Authorization header.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials.strip()

    # 1. Check isolated dev-only demo token (strictly disabled in production)
    if token == DEV_DEMO_TOKEN:
        if IS_PRODUCTION:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Development demo credentials are strictly forbidden in production mode."
            )
        # Verify demo user exists in database
        with get_db() as conn:
            user = conn.execute(
                "SELECT id, username, email, full_name, role, is_active FROM users WHERE id = 'usr_demo_001';"
            ).fetchone()
            if user:
                return dict(user)

    # 2. Check active server-issued sessions
    session = ACTIVE_SESSIONS.get(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please authenticate."
        )

    if time.time() > session["expires_at"]:
        del ACTIVE_SESSIONS[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token has expired. Please log in again."
        )

    # Fetch user details from database
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, username, email, full_name, role, is_active FROM users WHERE id = ?;",
            (session["user_id"],)
        ).fetchone()
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated or no longer exists."
            )
        return dict(user)


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Dict[str, Any]:
    """
    Return authenticated user or fall back to local demo patient for unauthenticated guest game sessions.
    Allows students/professors to immediately play without barrier.
    """
    try:
        if credentials and credentials.credentials:
            return get_current_user(credentials)
    except Exception:
        pass

    with get_db() as conn:
        user = conn.execute(
            "SELECT id, username, email, full_name, role, is_active FROM users WHERE id = 'usr_demo_001';"
        ).fetchone()
        if user:
            return dict(user)

    return {"id": "usr_demo_001", "username": "demouser", "full_name": "Health Explorer", "role": "demo_user"}

