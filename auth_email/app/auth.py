from datetime import datetime, timedelta, timezone

import hmac
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .email_service import send_verification_email
from .models import EmailOTP, User, utcnow
from .security import (
    create_access_token,
    decode_access_token,
    generate_otp,
    hash_otp,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)

GENERIC_SENT = {"message": "If this email can be used, a verification code has been sent."}


# ---------- schemas ----------
class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt ignores bytes past 72


class VerifyIn(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")


class EmailIn(BaseModel):
    email: EmailStr


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=72)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- helpers ----------
def _norm(email: str) -> str:
    return email.strip().lower()


def _aware(dt: datetime) -> datetime:
    # SQLite returns naive datetimes; Postgres returns aware ones. Normalise.
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _get_user(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def issue_otp(db: Session, user: User) -> str | None:
    """Create a fresh code for the user. Returns None if still in the resend cooldown."""
    now = utcnow()
    existing = db.scalar(select(EmailOTP).where(EmailOTP.user_id == user.id))
    if existing:
        next_allowed = _aware(existing.last_sent_at) + timedelta(
            seconds=settings.otp_resend_cooldown_seconds
        )
        if now < next_allowed:
            return None
        db.delete(existing)
        db.flush()

    code = generate_otp()
    db.add(
        EmailOTP(
            user_id=user.id,
            code_hash=hash_otp(code),
            expires_at=now + timedelta(minutes=settings.otp_ttl_minutes),
            attempts=0,
            last_sent_at=now,
        )
    )
    db.commit()
    return code


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    if creds is None:
        raise unauthorized
    user_id = decode_access_token(creds.credentials)
    if user_id is None:
        raise unauthorized
    user = db.get(User, user_id)
    if user is None or not user.is_verified:
        raise unauthorized
    return user


# ---------- routes ----------
@router.post("/signup", status_code=status.HTTP_202_ACCEPTED)
def signup(body: SignupIn, bg: BackgroundTasks, db: Session = Depends(get_db)):
    email = _norm(body.email)
    user = _get_user(db, email)

    if user is None:
        user = User(email=email, password_hash=hash_password(body.password))
        db.add(user)
        try:
            db.commit()
        except IntegrityError:  # two signups racing for the same email
            db.rollback()
            user = _get_user(db, email)

    # Same response whether the email is new, unverified or already verified,
    # so the endpoint can't be used to discover who has an account.
    if user is not None and not user.is_verified:
        code = issue_otp(db, user)
        if code:
            bg.add_task(send_verification_email, user.email, code)

    return GENERIC_SENT


@router.post("/resend-code")
def resend_code(body: EmailIn, bg: BackgroundTasks, db: Session = Depends(get_db)):
    user = _get_user(db, _norm(body.email))
    if user is not None and not user.is_verified:
        code = issue_otp(db, user)  # None during cooldown -> silently skipped
        if code:
            bg.add_task(send_verification_email, user.email, code)
    return GENERIC_SENT


@router.post("/verify-email", response_model=TokenOut)
def verify_email(body: VerifyIn, db: Session = Depends(get_db)):
    invalid = HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired code")

    user = _get_user(db, _norm(body.email))
    if user is None or user.is_verified:
        raise invalid

    otp = db.scalar(
        select(EmailOTP).where(EmailOTP.user_id == user.id).with_for_update()
    )
    if otp is None:
        raise invalid

    if _aware(otp.expires_at) < utcnow() or otp.attempts >= settings.otp_max_attempts:
        db.delete(otp)
        db.commit()
        raise invalid

    if not hmac.compare_digest(otp.code_hash, hash_otp(body.code)):
        otp.attempts += 1
        if otp.attempts >= settings.otp_max_attempts:
            db.delete(otp)  # too many wrong guesses: kill the code
        db.commit()
        raise invalid

    user.is_verified = True
    db.delete(otp)
    db.commit()
    return TokenOut(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = _get_user(db, _norm(body.email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "email_not_verified")
    return TokenOut(access_token=create_access_token(user.id))


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "is_verified": user.is_verified}
