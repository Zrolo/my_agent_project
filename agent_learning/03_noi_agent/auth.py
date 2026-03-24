"""
Minimal authentication for NOI Agent API
"""

import hashlib
import json
import os
import secrets
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, "accounts.json")

# In-memory token storage: {token: {"user_id": str, "role": str}}
tokens = {}

security = HTTPBearer(auto_error=False)


def load_accounts() -> dict:
    """Load user accounts from JSON file"""
    if not os.path.exists(ACCOUNTS_FILE):
        return {}
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_password(plain_password: str, password_hash: str, salt: str) -> bool:
    """Verify password using PBKDF2"""
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return hashed == password_hash


def authenticate_user(user_id: str, password: str) -> Optional[dict]:
    """Authenticate user and return user info if valid"""
    accounts = load_accounts()
    user = accounts.get(user_id)
    if not user:
        return None
    if verify_password(password, user["password_hash"], user["salt"]):
        return {"id": user["id"], "role": user["role"]}
    return None


def create_token(user_id: str, role: str) -> str:
    """Create a new auth token"""
    token = secrets.token_urlsafe(32)
    tokens[token] = {"user_id": user_id, "role": role}
    return token


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """FastAPI dependency to get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    token_data = tokens.get(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


def require_teacher(user: dict = Depends(get_current_user)) -> dict:
    """FastAPI dependency to require teacher role"""
    if user["role"] != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher role required",
        )
    return user


def require_student(user: dict = Depends(get_current_user)) -> dict:
    """FastAPI dependency to require student role"""
    if user["role"] != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student role required",
        )
    return user
