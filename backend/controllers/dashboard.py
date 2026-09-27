from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException

from database import get_connection
from controllers.common import database_error, get_current_user

router = APIRouter()


def monthly_goal(connection, cursor, user_id, target=None):
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_goals (
        user_id INT NOT NULL,
        goal_month CHAR(7) NOT NULL,
        target_kg DECIMAL(12,3) NOT NULL DEFAULT 100,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, goal_month)
    ) ENGINE=InnoDB""")
    month = date.today().strftime("%Y-%m")
    if target is not None:
        cursor.execute(
            """INSERT INTO user_goals (user_id, goal_month, target_kg) VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE target_kg = VALUES(target_kg)""",
            (user_id, month, target),
        )
    cursor.execute("SELECT target_kg FROM user_goals WHERE user_id = %s AND goal_month = %s", (user_id, month))
    row = cursor.fetchone()
    return float(row["target_kg"] if isinstance(row, dict) else row[0]) if row else 100.0


def monthly_totals(cursor, user_id):
    cursor.execute(
        """SELECT COALESCE(SUM(c.co2e), 0) AS total_co2e, COUNT(a.id) AS total_activities,
                  COALESCE(SUM(CASE WHEN a.category='travel' THEN c.co2e ELSE 0 END), 0) AS travel_co2e,
                  COALESCE(SUM(CASE WHEN a.category='electricity' THEN c.co2e ELSE 0 END), 0) AS electricity_co2e,
                  COALESCE(SUM(CASE WHEN a.category='food' THEN c.co2e ELSE 0 END), 0) AS food_co2e
           FROM activities a JOIN carbon_records c ON c.activity_id = a.id
           WHERE a.user_id = %s
             AND a.activity_date >= DATE_SUB(CURDATE(), INTERVAL (DAYOFMONTH(CURDATE()) - 1) DAY)
             AND a.activity_date < DATE_ADD(LAST_DAY(CURDATE()), INTERVAL 1 DAY)""",
        (user_id,),
    )
    return cursor.fetchone()


def progress(current, target):
    return {
        "target": target, "current": current,
        "progress": round(current / target * 100, 1) if target else 0,
        "remaining": round(max(target - current, 0), 3),
        "target_co2e": target, "used_co2e": current,
        "progress_percent": round(current / target * 100, 1) if target else 0,
        "remaining_co2e": round(max(target - current, 0), 3),
    }


@router.get("/dashboard")
def get_dashboard(user=Depends(get_current_user)):
    connection = cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        goal = monthly_goal(connection, cursor, user["id"])
        row = monthly_totals(cursor, user["id"])
        target = float(goal)
        current = float(row["total_co2e"] or 0)
        goal_data = progress(current, target)
        today = date.today()
        month_start = today.replace(day=1)
        previous_month_end = month_start - timedelta(days=1)
        previous_month_start = previous_month_end.replace(day=1)
        cursor.execute(
            """SELECT COALESCE(SUM(c.co2e), 0) AS total_co2e,
                      COALESCE(SUM(CASE WHEN a.category='travel' THEN c.co2e ELSE 0 END), 0) AS travel_co2e,
                      COALESCE(SUM(CASE WHEN a.category='electricity' THEN c.co2e ELSE 0 END), 0) AS electricity_co2e,
                      COALESCE(SUM(CASE WHEN a.category='food' THEN c.co2e ELSE 0 END), 0) AS food_co2e
               FROM activities a JOIN carbon_records c ON c.activity_id = a.id
               WHERE a.user_id = %s AND a.activity_date >= %s AND a.activity_date < %s""",
            (user["id"], previous_month_start, month_start),
        )
        previous_row = cursor.fetchone()
        previous = float(previous_row["total_co2e"] or 0)
        previous_categories = {
            "travel": float(previous_row["travel_co2e"] or 0),
            "electricity": float(previous_row["electricity_co2e"] or 0),
            "food": float(previous_row["food_co2e"] or 0),
        }
        reduction = round((previous - current) / previous * 100, 1) if previous > 0 else None
        return {
            "total_co2": current, "total_co2e": current,
            "travel": float(row["travel_co2e"] or 0), "travel_co2e": float(row["travel_co2e"] or 0),
            "electricity": float(row["electricity_co2e"] or 0), "electricity_co2e": float(row["electricity_co2e"] or 0),
            "food": float(row["food_co2e"] or 0), "food_co2e": float(row["food_co2e"] or 0),
            "activities": int(row["total_activities"] or 0), "total_activities": int(row["total_activities"] or 0),
            "reduction": reduction, "reduction_percent": reduction,
            "has_previous_month_data": previous > 0,
            "current_month": {"start": month_start.isoformat(), "through": today.isoformat(), "label": today.strftime("%B %Y"), "period": "month_to_date", "total_co2e": round(current, 3)},
            "previous_month": {
                "start": previous_month_start.isoformat(), "through": previous_month_end.isoformat(),
                "label": previous_month_start.strftime("%B %Y"), "total_co2e": round(previous, 3),
                "has_data": previous > 0, "categories": previous_categories,
            },
            "goal": goal_data, "goal_progress": goal_data,
        }
    except Exception as error:
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@router.get("/goals/monthly")
def get_goal(user=Depends(get_current_user)):
    connection = cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        target = monthly_goal(connection, cursor, user["id"])
        row = monthly_totals(cursor, user["id"])
        return progress(float(row["total_co2e"] or 0), target)
    except Exception as error:
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@router.put("/goals/monthly")
def update_goal(payload: dict, user=Depends(get_current_user)):
    target = payload.get("target", payload.get("target_kg", payload.get("target_co2e")))
    try:
        target = float(target)
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail="target must be a positive number") from error
    if not 1 <= target <= 100000:
        raise HTTPException(status_code=422, detail="target must be between 1 and 100000 kg CO2e")
    connection = cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        monthly_goal(connection, cursor, user["id"], target)
        row = monthly_totals(cursor, user["id"])
        connection.commit()
        return progress(float(row["total_co2e"] or 0), target)
    except Exception as error:
        if connection:
            connection.rollback()
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
