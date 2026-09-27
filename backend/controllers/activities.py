from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, root_validator

from database import get_connection
from services.calculator import calculate_carbon
from controllers.common import database_error, get_current_user

router = APIRouter()


class ActivityRequest(BaseModel):
    category: str
    activity: str | None = None
    activity_type: str | None = None
    amount: float | None = None
    value: float | None = None
    unit: str
    date: Date | None = None
    activity_date: Date | None = None

    @root_validator(pre=True)
    def normalize_contract_aliases(cls, values):
        values = dict(values or {})
        values.setdefault("activity", values.get("activity_type"))
        values.setdefault("amount", values.get("value"))
        values.setdefault("date", values.get("activity_date"))
        return values


@router.post("/activities", status_code=201)
def add_activity(request: ActivityRequest, user=Depends(get_current_user)):
    category = request.category.strip().lower()
    activity = (request.activity or "default").strip()
    activity_date = request.date or request.activity_date or Date.today()
    try:
        co2e = calculate_carbon(category, request.amount if request.amount is not None else request.value, activity, request.unit)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    connection = cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO activities
               (user_id, category, activity_type, value, unit, activity_date)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user["id"], category, activity, request.amount if request.amount is not None else request.value, request.unit, activity_date),
        )
        activity_id = cursor.lastrowid
        cursor.execute("INSERT INTO carbon_records (activity_id, co2e) VALUES (%s, %s)", (activity_id, co2e))
        connection.commit()
        return {
            "id": activity_id, "activity_id": activity_id, "category": category,
            "activity": activity, "activity_type": activity, "amount": request.amount if request.amount is not None else request.value,
            "value": request.amount if request.amount is not None else request.value, "unit": request.unit,
            "date": activity_date.isoformat(), "activity_date": activity_date.isoformat(),
            "co2e": co2e, "carbon_kg_co2e": co2e,
        }
    except Exception as error:
        if connection:
            connection.rollback()
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@router.get("/activities")
def get_activities(user=Depends(get_current_user)):
    connection = cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT a.id, a.category, a.activity_type, a.value, a.unit,
                      a.activity_date, c.co2e
               FROM activities a JOIN carbon_records c ON c.activity_id = a.id
               WHERE a.user_id = %s ORDER BY a.activity_date DESC, a.id DESC""",
            (user["id"],),
        )
        rows = cursor.fetchall()
        for row in rows:
            row["activity"] = row["activity_type"]
            row["amount"] = float(row["value"])
            row["value"] = float(row["value"])
            row["co2e"] = float(row["co2e"])
            row["date"] = row["activity_date"].isoformat() if hasattr(row["activity_date"], "isoformat") else str(row["activity_date"])
        return rows
    except Exception as error:
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
