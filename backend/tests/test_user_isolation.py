import pytest
from datetime import date
from tests.conftest import client, TestingSessionLocal


def register_user(client, name: str, email: str) -> str:
    res = client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": "Password12345!"},
    )
    assert res.status_code == 201
    return res.json()["access_token"]


def test_user_activity_isolation(client):
    """Ensure User A and User B only see their own activities."""
    token_a = register_user(client, "User Alpha", "alpha@example.com")
    token_b = register_user(client, "User Beta", "beta@example.com")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A records an activity
    client.post(
        "/api/activities",
        json={
            "category": "travel",
            "activity": "car",
            "amount": 20,
            "unit": "km",
            "date": "2026-09-27",
        },
        headers=headers_a,
    )

    # User B should see 0 activities
    res_b = client.get("/api/activities", headers=headers_b)
    assert res_b.status_code == 200
    assert len(res_b.json()) == 0

    # User A should see 1 activity
    res_a = client.get("/api/activities", headers=headers_a)
    assert res_a.status_code == 200
    assert len(res_a.json()) == 1


def test_user_dashboard_isolation(client):
    """Ensure User A's emissions do not appear on User B's dashboard."""
    token_a = register_user(client, "User A", "usera@example.com")
    token_b = register_user(client, "User B", "userb@example.com")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A records an activity
    client.post(
        "/api/activities",
        json={
            "category": "travel",
            "activity": "car",
            "amount": 20,
            "unit": "km",
            "date": date.today().isoformat(),
        },
        headers=headers_a,
    )

    dash_a = client.get("/api/dashboard", headers=headers_a).json()
    dash_b = client.get("/api/dashboard", headers=headers_b).json()

    assert dash_a["total_activities"] == 1
    assert dash_a["total_co2"] > 0
    assert dash_b["total_activities"] == 0
    assert dash_b["total_co2"] == 0.0


def test_user_goal_isolation(client):
    """Ensure User A's custom monthly goal target does not modify User B's goal target."""
    token_a = register_user(client, "Goal A", "goala@example.com")
    token_b = register_user(client, "Goal B", "goalb@example.com")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A updates monthly goal target to 250
    client.put("/api/goals/monthly", json={"target": 250.0}, headers=headers_a)

    goal_a = client.get("/api/goals/monthly", headers=headers_a).json()
    goal_b = client.get("/api/goals/monthly", headers=headers_b).json()

    assert goal_a["target"] == 250.0
    assert goal_b["target"] == 100.0  # Default


def test_user_trend_isolation(client):
    """Ensure User A's trend emissions do not appear on User B's trend."""
    token_a = register_user(client, "Trend A", "trenda@example.com")
    token_b = register_user(client, "Trend B", "trendb@example.com")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    today_str = date.today().isoformat()
    client.post(
        "/api/activities",
        json={
            "category": "travel",
            "activity": "car",
            "amount": 30,
            "unit": "km",
            "date": today_str,
        },
        headers=headers_a,
    )

    trend_a = client.get("/api/trend?period=7d", headers=headers_a).json()
    trend_b = client.get("/api/trend?period=7d", headers=headers_b).json()

    assert any(point["co2e"] > 0 for point in trend_a)
    assert all(point["co2e"] == 0.0 for point in trend_b)
