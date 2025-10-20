import json
import os
import secrets
import hashlib
from typing import Dict, Any, List, Optional

USERS_PATH = "data/users.json"

ITERATIONS = 200_000


def _load_users() -> List[Dict[str, Any]]:
    if not os.path.exists(USERS_PATH):
        return []
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_users(users: List[Dict[str, Any]]):
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def _hash_password(pw: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, ITERATIONS)
    return dk.hex()


def set_password(email: str, raw_password: str) -> None:
    users = _load_users()
    salt = secrets.token_bytes(16)
    pw_hash = _hash_password(raw_password, salt)
    # find user
    for u in users:
        if u.get("email") == email:
            u["salt"] = salt.hex()
            u["password_hash"] = pw_hash
            _save_users(users)
            return
    # new user default role wolf_rep
    users.append({
        "email": email,
        "display_name": email.split("@")[0].title(),
        "role": "wolf_rep",
        "owner_value": "Ivan Torres",
        "rep_phone": "+10000000000",
        "salt": salt.hex(),
        "password_hash": pw_hash
    })
    _save_users(users)


def verify_password(email: str, raw_password: str) -> Optional[Dict[str, Any]]:
    users = _load_users()
    for u in users:
        if u.get("email") == email and u.get("salt") and u.get("password_hash"):
            salt = bytes.fromhex(u.get("salt"))
            if _hash_password(raw_password, salt) == u.get("password_hash"):
                return u
    return None


def get_user(email: str) -> Optional[Dict[str, Any]]:
    for u in _load_users():
        if u.get("email") == email:
            return u
    return None


def list_users() -> List[Dict[str, Any]]:
    return _load_users()


def upsert_user(user: Dict[str, Any]) -> None:
    users = _load_users()
    for i, u in enumerate(users):
        if u.get("email") == user.get("email"):
            users[i] = user
            _save_users(users)
            return
    users.append(user)
    _save_users(users)
