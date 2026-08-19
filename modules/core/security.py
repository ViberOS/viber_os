"""Helpers simples de autenticação local do ViberOS."""
from __future__ import annotations

import hashlib
import hmac
import os

_ITERATIONS = 310_000


def hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return salt.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, expected_hex: str) -> bool:
    _, calculated = hash_password(password, salt_hex)
    return hmac.compare_digest(calculated, expected_hex)
