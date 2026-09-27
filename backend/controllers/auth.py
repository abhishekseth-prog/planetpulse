import hashlib
import hmac
import re
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from database import get_connection
from controllers.common import database_error, get_current_user, issue_token

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=254)
    password: str = Field(min_length=10, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return f"scrypt${salt.hex()}${digest.hex()}"


def check_password(password: str, stored: str) -> bool:
    try:
        algorithm, salt_hex, digest_hex = stored.split("$")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1, dklen=64)
        return hmac.compare_digest(actual.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def clean_email(email: str) -> str:
    normalized = email.strip().lower()
    if len(normalized) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized):
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    return normalized


def public_user(row):
    return {"id": int(row["id"]), "name": row["name"], "email": row["email"]}


@router.post("/register", status_code=201)
def register(payload: RegisterRequest):
    name = payload.name.strip()
    if len(name) < 2:
        raise HTTPException(status_code=422, detail="Name must contain at least 2 characters")
    email = clean_email(payload.email)
    connection = cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", (name, email, hash_password(payload.password)))
        user_id = cursor.lastrowid
        connection.commit()
        user = {"id": int(user_id), "name": name, "email": email}
        return {"access_token": issue_token(user_id), "token_type": "bearer", "user": user}
    except HTTPException:
        if connection:
            connection.rollback()
        raise
    except Exception as error:
        if connection:
            connection.rollback()
        # A unique email index closes the concurrent-registration race.
        if getattr(error, "errno", None) == 1062:
            raise HTTPException(status_code=409, detail="An account with this email already exists") from error
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@router.post("/login")
def login(payload: LoginRequest):
    email = clean_email(payload.email)
    connection = cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if not row or not check_password(payload.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Email or password is incorrect")
        return {"access_token": issue_token(row["id"]), "token_type": "bearer", "user": public_user(row)}
    except HTTPException:
        raise
    except Exception as error:
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user
