import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import get_connection, get_cursor

bearer = HTTPBearer(auto_error=False)


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def issue_token(user_id: int) -> str:
    secret = os.getenv("JWT_SECRET_KEY", "")
    if len(secret) < 32:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    now = int(time.time())
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64(json.dumps({"sub": str(user_id), "iat": now, "exp": now + 60 * 60 * 12}, separators=(",", ":")).encode())
    signing = f"{header}.{payload}"
    signature = _b64(hmac.new(secret.encode(), signing.encode(), hashlib.sha256).digest())
    return f"{signing}.{signature}"


def verify_token(token: str) -> int:
    secret = os.getenv("JWT_SECRET_KEY", "")
    try:
        header, payload, signature = token.split(".")
        signing = f"{header}.{payload}"
        expected = _b64(hmac.new(secret.encode(), signing.encode(), hashlib.sha256).digest())
        if len(secret) < 32 or not hmac.compare_digest(signature, expected):
            raise ValueError
        decode = lambda part: json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
        if decode(header).get("alg") != "HS256":
            raise ValueError
        claims = decode(payload)
        if int(claims["exp"]) <= int(time.time()):
            raise ValueError
        return int(claims["sub"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Sign in to continue")
    user_id = verify_token(credentials.credentials)
    connection = cursor = None
    try:
        connection = get_connection()
        cursor = get_cursor(connection, dictionary=True)
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Account is no longer available")
        return {"id": int(user["id"]), "name": user["name"], "email": user["email"]}
    except HTTPException:
        raise
    except Exception as error:
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def database_error(error: Exception) -> HTTPException:
    # Keep database credentials, SQL, and driver diagnostics out of client responses.
    return HTTPException(status_code=503, detail="PlanetPulse data store is unavailable")
