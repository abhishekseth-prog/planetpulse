"""Local end-to-end verification for PlanetPulse auth and private APIs.

Runs against the configured local MySQL and API, then removes only the two
temporary accounts and rows created by this verification run.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
from datetime import date, timedelta
from pathlib import Path
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database import get_connection

BASE = os.getenv("PLANETPULSE_TEST_URL", "http://127.0.0.1:8001/api")
ids = []


def call(path, method="GET", body=None, token=None, expected=200):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            status, content = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, content = error.code, error.read()
    assert status == expected, f"{method} {path}: expected {expected}, got {status}"
    return json.loads(content) if content else {}


def expired_token(user_id):
    def encode(value):
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode()
    secret = os.environ["JWT_SECRET_KEY"].encode()
    header = encode(b'{"alg":"HS256","typ":"JWT"}')
    payload = encode(json.dumps({"sub": str(user_id), "iat": 1, "exp": 2}, separators=(",", ":")).encode())
    signing = f"{header}.{payload}"
    signature = encode(hmac.new(secret, signing.encode(), hashlib.sha256).digest())
    return f"{signing}.{signature}"


def verify():
    assert call("/health")["status"] == "ok"
    schema_connection = get_connection()
    schema_cursor = schema_connection.cursor(dictionary=True)
    schema_cursor.execute(
        """SELECT table_name AS table_name, column_name AS column_name, column_type AS column_type FROM information_schema.columns
           WHERE table_schema = DATABASE()
             AND table_name IN ('users', 'activities', 'carbon_records', 'user_goals')
           ORDER BY table_name, ordinal_position"""
    )
    schema_columns = schema_cursor.fetchall()
    schema_cursor.execute(
        """SELECT table_name AS table_name, constraint_name AS constraint_name,
                  column_name AS column_name, referenced_table_name AS referenced_table_name
           FROM information_schema.key_column_usage WHERE constraint_schema = DATABASE()
             AND table_name IN ('activities', 'carbon_records', 'user_goals')
           ORDER BY table_name, constraint_name"""
    )
    schema_keys = schema_cursor.fetchall()
    schema_cursor.close()
    schema_connection.close()
    print("MySQL columns:", [(row["table_name"], row["column_name"], row["column_type"]) for row in schema_columns])
    print("MySQL foreign keys:", [(row["table_name"], row["column_name"], row["referenced_table_name"]) for row in schema_keys if row["referenced_table_name"]])
    invalid_password = secrets.token_urlsafe(20)
    weak_password = secrets.token_urlsafe(4)
    call("/auth/register", "POST", {"name": "QA User", "email": "not-an-email", "password": invalid_password}, expected=422)
    call("/auth/register", "POST", {"name": "QA User", "email": "weak@example.invalid", "password": weak_password}, expected=422)
    call("/auth/register", "POST", {"email": "missing@example.invalid"}, expected=422)
    call("/auth/login", "POST", {"email": "missing@example.invalid"}, expected=422)
    call("/auth/login", "POST", {"email": "unknown@example.invalid", "password": invalid_password}, expected=401)
    print("PASS invalid email, weak password, missing fields, and unknown login are rejected")
    suffix = secrets.token_hex(8)
    password = f"Vfy-{secrets.token_urlsafe(18)}"
    accounts = []
    try:
        for display in ("Test Account A", "Test Account B"):
            email = f"pp-e2e-{suffix}-{len(accounts)}@example.invalid"
            result = call("/auth/register", "POST", {"name": display, "email": email, "password": password}, expected=201)
            accounts.append((result["user"], result["access_token"], email))
            ids.append(result["user"]["id"])
        print("PASS register creates two isolated accounts")

        user_a, token_a, email_a = accounts[0]
        user_b, token_b, _ = accounts[1]
        call("/auth/register", "POST", {"name": "Duplicate", "email": email_a, "password": password}, expected=409)
        call("/auth/login", "POST", {"email": email_a, "password": secrets.token_urlsafe(20)}, expected=401)
        print("PASS duplicate registration and invalid login are rejected")

        call("/dashboard", expected=401)
        call("/dashboard", token="invalid.token.value", expected=401)
        call("/dashboard", token=expired_token(user_a["id"]), expected=401)
        call("/activities", expected=401)
        call("/trend?period=7d", expected=401)
        call("/goals/monthly", expected=401)
        call("/insights", expected=401)
        call("/what-if", "POST", {"current_activity": "Car", "alternative_activity": "Metro", "distance": 20}, expected=401)
        assert call("/auth/me", token=token_a)["id"] == user_a["id"]
        print("PASS missing, invalid, and expired tokens are rejected; /auth/me works")

        dashboard_b = call("/dashboard", token=token_b)
        assert dashboard_b["total_activities"] == 0
        assert call("/activities", token=token_b) == []
        goal_a = call("/goals/monthly", token=token_a)
        assert call("/goals/monthly", "PUT", {"target": 321}, token_a)["target"] == 321
        assert call("/goals/monthly", token=token_b)["target"] == 100
        print("PASS protected dashboard, activities, and goals are account-scoped")

        activity = call("/activities", "POST", {
            "category": "travel", "activity": "car", "amount": 10,
            "unit": "km", "date": date.today().isoformat(),
        }, token_a, expected=201)
        assert activity["co2e"] == 2.9
        electricity = call("/activities", "POST", {
            "category": "electricity", "activity": "Air conditioner", "amount": 2,
            "unit": "hours", "date": date.today().isoformat(),
        }, token_a, expected=201)
        assert electricity["co2e"] == 1.718
        food = call("/activities", "POST", {
            "category": "food", "activity": "Chicken meal", "amount": 1,
            "unit": "meal", "date": date.today().isoformat(),
        }, token_a, expected=201)
        assert food["co2e"] == 1.5
        call("/activities", "POST", {"category": "travel", "activity": "car", "amount": 0, "unit": "km"}, token_a, expected=422)
        call("/activities", "POST", {"category": "travel", "activity": "car", "amount": -5, "unit": "km"}, token_a, expected=422)
        call("/activities", "POST", {"category": "travel", "activity": "car", "amount": 5, "unit": "miles"}, token_a, expected=422)
        call("/activities", "POST", {"category": "electricity", "activity": "Air conditioner", "amount": 25, "unit": "hours"}, token_a, expected=422)
        forged_owner = call("/activities", "POST", {
            "category": "food", "activity": "Plant-based meal", "amount": 1,
            "unit": "meal", "user_id": user_b["id"],
        }, token_a, expected=201)
        assert forged_owner["category"] == "food"
        assert len(call("/activities", token=token_a)) == 4
        previous_month_day = (date.today().replace(day=1) - timedelta(days=1)).replace(day=15)
        previous_month_activity = call("/activities", "POST", {
            "category": "travel", "activity": "car", "amount": 10,
            "unit": "km", "date": previous_month_day.isoformat(),
        }, token_a, expected=201)
        assert call("/activities", token=token_b) == []
        dashboard_a = call("/dashboard", token=token_a)
        dashboard_b = call("/dashboard", token=token_b)
        assert dashboard_b["total_activities"] == 0
        assert dashboard_b["travel_co2e"] == dashboard_b["electricity_co2e"] == dashboard_b["food_co2e"] == 0
        assert dashboard_a["total_activities"] == 4
        assert dashboard_a["has_previous_month_data"] is True
        assert dashboard_a["previous_month"]["total_co2e"] == 2.9
        assert dashboard_a["previous_month"]["categories"]["travel"] == 2.9
        assert dashboard_a["current_month"]["through"] == date.today().isoformat()
        assert dashboard_b["has_previous_month_data"] is False
        assert dashboard_b["reduction_percent"] is None
        stored_rows = call("/activities", token=token_a)
        print("Persisted CO2e:", [(row["category"], row["co2e"]) for row in stored_rows])
        by_id = {row["id"]: row["co2e"] for row in stored_rows}
        assert by_id[activity["id"]] == activity["co2e"]
        assert by_id[electricity["id"]] == electricity["co2e"]
        assert by_id[food["id"]] == food["co2e"]
        assert by_id[forged_owner["id"]] == forged_owner["co2e"]
        assert by_id[previous_month_activity["id"]] == previous_month_activity["co2e"]
        current_month_key = date.today().strftime("%Y-%m")
        current_rows = [row for row in stored_rows if row["activity_date"].startswith(current_month_key)]
        assert dashboard_a["travel_co2e"] == sum(row["co2e"] for row in current_rows if row["category"] == "travel"), dashboard_a
        assert dashboard_a["electricity_co2e"] == sum(row["co2e"] for row in current_rows if row["category"] == "electricity"), dashboard_a
        assert dashboard_a["food_co2e"] == sum(row["co2e"] for row in current_rows if row["category"] == "food"), dashboard_a
        trend = call("/trend?period=7d", token=token_a)
        assert len(trend) == 7 and any(point["co2e"] > 0 for point in trend)
        assert any(point["co2e"] == 0 for point in trend)
        trend_b = call("/trend?period=7d", token=token_b)
        assert len(trend_b) == 7 and all(point["co2e"] == 0 for point in trend_b)
        call("/trend?period=invalid", token=token_a, expected=422)
        print("PASS all activity categories, validation, forged user_id rejection, dashboard totals, and trend")

        what_if = call("/what-if", "POST", {
            "current_activity": "Car", "alternative_activity": "Metro", "distance": 20,
        }, token_a)
        assert what_if["daily_reduction"] == round(what_if["current_co2"] - what_if["new_co2"], 3)
        call("/what-if", "POST", {
            "category": "travel",
            "current": {"activity": "Car", "amount": 20, "unit": "km"},
            "alternative": {"activity": "Beef meal", "amount": 20, "unit": "km"},
        }, token_a, expected=422)
        call("/what-if", "POST", {
            "category": "travel",
            "current": {"activity": "Car", "amount": -1, "unit": "km"},
            "alternative": {"activity": "Metro", "amount": 20, "unit": "km"},
        }, token_a, expected=422)
        insights_a = call("/insights", token=token_a)
        insights_b = call("/insights", token=token_b)
        assert insights_a["period"] == "current_month" and insights_a["method"] == "rule_based"
        assert insights_a["observation"] == "Travel is currently your largest emission category."
        assert insights_a["contribution_percent"] > 0
        assert insights_a["potential_impact_kg"] is None
        assert len(insights_a["recent_activities"]) == 5
        assert insights_a["monthly_goal"]["target"] == 321
        assert insights_b["contribution_percent"] == 0
        assert insights_b["has_activities"] is False and insights_b["actions"] == []
        assert insights_b["largest_contributor"] is None
        assert "Start tracking your activities" in insights_b["opportunity"]
        electricity_update = call("/activities", "POST", {
            "category": "electricity", "activity": "Air conditioner", "amount": 20,
            "unit": "hours", "date": date.today().isoformat(),
        }, token_a, expected=201)
        assert call("/insights", token=token_a)["largest_contributor"] == "Electricity"
        food_update = call("/activities", "POST", {
            "category": "food", "activity": "Beef meal", "amount": 10,
            "unit": "meal", "date": date.today().isoformat(),
        }, token_a, expected=201)
        food_insights = call("/insights", token=token_a)
        assert food_insights["largest_contributor"] == "Food"
        assert food_insights["category_totals"]["food"] >= food_update["co2e"]
        assert call("/insights", token=token_b)["has_activities"] is False
        print("PASS What-If uses shared engine values, rejects invalid comparisons, and insights are authenticated")

        login = call("/auth/login", "POST", {"email": email_a, "password": password})
        assert call("/auth/me", token=login["access_token"])["id"] == user_a["id"]
        print("PASS login restores a valid authenticated session")
    finally:
        if ids:
            connection = get_connection()
            cursor = connection.cursor()
            try:
                placeholders = ",".join(["%s"] * len(ids))
                cursor.execute(f"DELETE c FROM carbon_records c JOIN activities a ON a.id=c.activity_id WHERE a.user_id IN ({placeholders})", tuple(ids))
                cursor.execute(f"DELETE FROM activities WHERE user_id IN ({placeholders})", tuple(ids))
                cursor.execute(f"DELETE FROM user_goals WHERE user_id IN ({placeholders})", tuple(ids))
                cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders})", tuple(ids))
                connection.commit()
            finally:
                cursor.close()
                connection.close()
            print("CLEANUP temporary verification accounts and rows removed")


if __name__ == "__main__":
    verify()
