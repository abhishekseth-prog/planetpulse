import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Optional, Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.config import JWT_SECRET_KEY, JWT_EXPIRATION_SECONDS
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest


def _b64(value: bytes) -> str:
    """Base64url encode bytes without padding."""
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def hash_password(password: str) -> str:
    """Hash password using cryptographically strong salted scrypt."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return f"scrypt${salt.hex()}${digest.hex()}"


def check_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored scrypt hash."""
    try:
        algorithm, salt_hex, digest_hex = stored_hash.split("$")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=2**14,
            r=8,
            p=1,
            dklen=64,
        )
        return hmac.compare_digest(actual.hex(), digest_hex)
    except Exception:
        return False


def create_access_token(user_id: int) -> str:
    """Generate a signed HMAC-SHA256 JWT access token."""
    secret = JWT_SECRET_KEY
    if len(secret) < 32:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    now = int(time.time())
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode("utf-8"))
    payload = _b64(
        json.dumps(
            {"sub": str(user_id), "iat": now, "exp": now + JWT_EXPIRATION_SECONDS},
            separators=(",", ":"),
        ).encode("utf-8")
    )
    signing_input = f"{header}.{payload}"
    signature = _b64(hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest())
    return f"{signing_input}.{signature}"


def verify_access_token(token: str) -> int:
    """Validate signed JWT access token and return user_id."""
    secret = JWT_SECRET_KEY
    try:
        header, payload, signature = token.split(".")
        signing_input = f"{header}.{payload}"
        expected_sig = _b64(
            hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
        )
        if len(secret) < 32 or not hmac.compare_digest(signature, expected_sig):
            raise ValueError("Signature mismatch")

        def decode_part(part: str):
            return json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))

        hdr = decode_part(header)
        if hdr.get("alg") != "HS256":
            raise ValueError("Unsupported algorithm")
        claims = decode_part(payload)
        if int(claims.get("exp", 0)) <= int(time.time()):
            raise ValueError("Token expired")
        return int(claims["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")


def register_user(db: Session, request: RegisterRequest) -> Tuple[User, str]:
    """Register a new user account."""
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    new_user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(new_user.id)
    return new_user, token


def authenticate_user(db: Session, request: LoginRequest) -> Tuple[User, str]:
    """Authenticate existing user credentials."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not check_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")

    token = create_access_token(user.id)
    return user, token
