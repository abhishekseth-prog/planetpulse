import pytest
from tests.conftest import client, TestingSessionLocal
from app.services.auth_service import hash_password, check_password


def test_password_hashing():
    """Verify scrypt password hashing and verification."""
    password = "SuperSecretPassword123"
    hashed = hash_password(password)
    assert hashed.startswith("scrypt$")
    assert check_password(password, hashed) is True
    assert check_password("WrongPassword", hashed) is False


def test_user_registration_success(client):
    """POST /api/auth/register creates user and returns JWT token."""
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "StrongPassword123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["name"] == "Test User"
    assert data["user"]["email"] == "testuser@example.com"
    assert "id" in data["user"]


def test_duplicate_email_registration_fails(client):
    """POST /api/auth/register with duplicate email returns 409 Conflict."""
    payload = {
        "name": "First User",
        "email": "duplicate@example.com",
        "password": "StrongPassword123!",
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_weak_password_registration_fails(client):
    """POST /api/auth/register with short password returns 422 Unprocessable Entity."""
    payload = {
        "name": "Weak User",
        "email": "weak@example.com",
        "password": "short",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_invalid_email_registration_fails(client):
    """POST /api/auth/register with invalid email format returns 422."""
    payload = {
        "name": "Invalid Email",
        "email": "not-an-email",
        "password": "StrongPassword123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_user_login_success(client):
    """POST /api/auth/login with valid credentials returns token."""
    register_payload = {
        "name": "Login User",
        "email": "loginuser@example.com",
        "password": "ValidPassword123!",
    }
    client.post("/api/auth/register", json=register_payload)

    login_payload = {
        "email": "loginuser@example.com",
        "password": "ValidPassword123!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "loginuser@example.com"


def test_user_login_invalid_password(client):
    """POST /api/auth/login with incorrect password returns 401."""
    register_payload = {
        "name": "Login User 2",
        "email": "loginuser2@example.com",
        "password": "ValidPassword123!",
    }
    client.post("/api/auth/register", json=register_payload)

    login_payload = {
        "email": "loginuser2@example.com",
        "password": "WrongPassword999!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_user_login_nonexistent_email(client):
    """POST /api/auth/login with non-existent email returns 401."""
    login_payload = {
        "email": "nobody@example.com",
        "password": "SomePassword123!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401


def test_get_current_user_profile(client):
    """GET /api/auth/me returns authenticated user's profile."""
    register_payload = {
        "name": "Profile User",
        "email": "profile@example.com",
        "password": "ProfilePassword123!",
    }
    res = client.post("/api/auth/register", json=register_payload)
    token = res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Profile User"
    assert data["email"] == "profile@example.com"


def test_get_current_user_profile_unauthorized(client):
    """GET /api/auth/me without token returns 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_current_user_profile_invalid_token(client):
    """GET /api/auth/me with invalid token returns 401."""
    headers = {"Authorization": "Bearer invalid.token.value"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
