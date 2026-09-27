from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query

from database import get_connection
from controllers.common import database_error, get_current_user

router = APIRouter()


@router.get("/trend")
def get_trend(period: str = Query("7d", pattern="^(7d|30d|3m)$"), user=Depends(get_current_user)):
    days = {"7d": 7, "30d": 30, "3m": 90}[period]
    connection = cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT CAST(a.activity_date AS CHAR) AS date,
                      ROUND(SUM(c.co2e), 3) AS co2e
               FROM activities a JOIN carbon_records c ON c.activity_id = a.id
               WHERE a.user_id = %s AND a.activity_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
               GROUP BY a.activity_date ORDER BY a.activity_date""",
            (user["id"], days - 1),
        )
        rows = cursor.fetchall()
        by_date = {str(row["date"]): float(row["co2e"] or 0) for row in rows}
        today = date.today()
        first_day = today - timedelta(days=days - 1)
        return [
            {"date": (first_day + timedelta(days=offset)).isoformat(),
             "label": (first_day + timedelta(days=offset)).strftime("%a" if days == 7 else "%d %b"),
             "co2e": by_date.get((first_day + timedelta(days=offset)).isoformat(), 0.0)}
            for offset in range(days)
        ]
    except Exception as error:
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
