"""
Minimal authentication for NOI Agent API
"""

import hashlib
import json
import os
import secrets
import tempfile
import time
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


def hash_password(plain_password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()


def verify_password(plain_password: str, password_hash: str, salt: str) -> bool:
    """Verify password using PBKDF2"""
    hashed = hash_password(plain_password, salt)
    return hashed == password_hash


def save_accounts_atomic(accounts: dict) -> None:
    """Persist accounts without leaving a half-written JSON file."""
    directory = os.path.dirname(ACCOUNTS_FILE)
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix="accounts.", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp_path, ACCOUNTS_FILE)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def is_account_active(user_id: str) -> bool:
    accounts = load_accounts()
    account = accounts.get(user_id)
    if not account:
        return True
    return account.get("active", True) is not False


def _public_student_account(user_id: str, account: dict) -> dict:
    return {
        "user_id": user_id,
        "display_name": account.get("display_name") or account.get("name") or user_id,
        "role": account.get("role") or "student",
        "active": account.get("active", True) is not False,
        "created_at": account.get("created_at") or "",
        "updated_at": account.get("updated_at") or "",
    }


def list_student_accounts() -> list[dict]:
    accounts = load_accounts()
    students = [
        _public_student_account(user_id, account)
        for user_id, account in accounts.items()
        if account.get("role") == "student"
    ]
    return sorted(students, key=lambda item: item["user_id"])


def _validate_user_id(user_id: str) -> str:
    normalized = (user_id or "").strip()
    if not normalized:
        return ""
    if len(normalized) > 40 or not all(ch.isalnum() or ch in "_-" for ch in normalized):
        raise ValueError("登录账号只能使用字母、数字、下划线或短横线，长度不超过 40 个字符")
    return normalized


def _generate_unique_student_id(accounts: dict) -> str:
    for _ in range(20):
        candidate = f"stu{secrets.randbelow(900000) + 100000}"
        if candidate not in accounts:
            return candidate
    raise ValueError("自动生成账号失败，请手动填写登录账号")


def _generate_password() -> str:
    alphabet = "abcdefghijkmnpqrstuvwxyz23456789"
    return "".join(secrets.choice(alphabet) for _ in range(10))


def create_student_account(display_name: str, user_id: str = "", password: str = "") -> dict:
    accounts = load_accounts()
    name = (display_name or "").strip()
    if not name:
        raise ValueError("请填写显示姓名")

    normalized_user_id = _validate_user_id(user_id) or _generate_unique_student_id(accounts)
    if normalized_user_id in accounts:
        raise ValueError("这个登录账号已经存在，请换一个")

    plain_password = (password or "").strip() or _generate_password()
    if len(plain_password) < 4:
        raise ValueError("密码至少需要 4 个字符")

    salt = secrets.token_hex(16)
    now = str(int(time.time()))
    accounts[normalized_user_id] = {
        "id": normalized_user_id,
        "display_name": name,
        "password_hash": hash_password(plain_password, salt),
        "salt": salt,
        "role": "student",
        "active": True,
        "created_at": now,
        "updated_at": now,
    }
    save_accounts_atomic(accounts)
    public_account = _public_student_account(normalized_user_id, accounts[normalized_user_id])
    public_account["password"] = plain_password
    return public_account


def reset_student_password(user_id: str, password: str = "") -> dict:
    accounts = load_accounts()
    account = accounts.get(user_id)
    if not account or account.get("role") != "student":
        raise ValueError("未找到这个学生账号")

    plain_password = (password or "").strip() or _generate_password()
    if len(plain_password) < 4:
        raise ValueError("密码至少需要 4 个字符")

    salt = secrets.token_hex(16)
    account["password_hash"] = hash_password(plain_password, salt)
    account["salt"] = salt
    account["updated_at"] = str(int(time.time()))
    save_accounts_atomic(accounts)
    public_account = _public_student_account(user_id, account)
    public_account["password"] = plain_password
    return public_account


def change_own_password(user_id: str, current_password: str, new_password: str) -> None:
    accounts = load_accounts()
    account = accounts.get(user_id)
    if not account:
        raise ValueError("未找到当前账号")

    current_plain = current_password or ""
    if not verify_password(current_plain, account["password_hash"], account["salt"]):
        raise ValueError("当前密码不正确")

    new_plain = (new_password or "").strip()
    if len(new_plain) < 4:
        raise ValueError("新密码至少需要 4 个字符")

    salt = secrets.token_hex(16)
    account["password_hash"] = hash_password(new_plain, salt)
    account["salt"] = salt
    account["updated_at"] = str(int(time.time()))
    save_accounts_atomic(accounts)


def set_student_active(user_id: str, active: bool) -> dict:
    accounts = load_accounts()
    account = accounts.get(user_id)
    if not account or account.get("role") != "student":
        raise ValueError("未找到这个学生账号")
    account["active"] = bool(active)
    account["updated_at"] = str(int(time.time()))
    save_accounts_atomic(accounts)
    return _public_student_account(user_id, account)


def authenticate_user(user_id: str, password: str) -> Optional[dict]:
    """Authenticate user and return user info if valid"""
    accounts = load_accounts()
    user = accounts.get(user_id)
    if not user:
        return None
    if user.get("active", True) is False:
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

    if not is_account_active(token_data["user_id"]):
        tokens.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号已停用，请联系老师",
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
