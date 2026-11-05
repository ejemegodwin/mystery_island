import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings


# ---------- passwords ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


# ---------- OTP ----------
def generate_otp() -> str:
    # secrets (not random) -> cryptographically secure
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(code: str) -> str:
    # Keyed hash: a 6-digit code has only 1M possibilities, so a plain hash
    # could be brute-forced instantly if the DB leaked. The secret key stops that.
    return hmac.new(settings.secret_key.encode(), code.encode(), hashlib.sha256).hexdigest()


# ---------- JWT ----------
def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
