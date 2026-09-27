from fastapi import APIRouter, Depends

from controllers.common import database_error
from controllers.dashboard import monthly_goal, monthly_totals, progress
from controllers.common import get_current_user
from database import get_connection

router = APIRouter()

RECOMMENDATIONS = {
    "travel": {
        "name": "Travel",
        "opportunity": "Replacing short car trips with public transport is your clearest opportunity.",
        "actions": [
            "Replace 2 short car trips with metro or bus",
            "Combine nearby errands into one journey",
            "Choose a lower-impact commute option once this week",
        ],
    },
    "electricity": {
        "name": "Electricity",
        "opportunity": "Reducing appliance use, especially cooling, is your clearest opportunity.",
        "actions": [
            "Reduce AC use by 1 hour a day",
            "Switch off appliances when they are idle",
            "Use an efficient setting for one appliance",
        ],
    },
    "food": {
        "name": "Food",
        "opportunity": "Choosing lower-impact meals is your clearest opportunity.",
        "actions": [
            "Choose 1 lower-impact meal this week",
            "Try a plant-based swap for one meal",
            "Plan portions to reduce food waste",
        ],
    },
}


@router.get("/insights")
def get_insights(user=Depends(get_current_user)):
    connection = cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        totals = monthly_totals(cursor, user["id"])
        categories = {
            "travel": float(totals["travel_co2e"] or 0),
            "electricity": float(totals["electricity_co2e"] or 0),
            "food": float(totals["food_co2e"] or 0),
        }
        total = float(totals["total_co2e"] or 0)
        activity_count = int(totals["total_activities"] or 0)
        has_emissions = total > 0
        has_activities = activity_count > 0
        goal_target = monthly_goal(connection, cursor, user["id"])
        goal_progress = progress(total, goal_target)

        cursor.execute(
            """SELECT COALESCE(SUM(CASE WHEN a.activity_date >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
                                               THEN c.co2e ELSE 0 END), 0) AS recent_total,
                      COALESCE(SUM(CASE WHEN a.activity_date < DATE_SUB(CURDATE(), INTERVAL 6 DAY)
                                               THEN c.co2e ELSE 0 END), 0) AS previous_total
               FROM activities a JOIN carbon_records c ON c.activity_id = a.id
               WHERE a.user_id = %s
                 AND a.activity_date >= DATE_SUB(CURDATE(), INTERVAL 13 DAY)
                 AND a.activity_date < DATE_ADD(CURDATE(), INTERVAL 1 DAY)""",
            (user["id"],),
        )
        trend_row = cursor.fetchone()
        recent_trend = float(trend_row["recent_total"] or 0)
        previous_trend = float(trend_row["previous_total"] or 0)
        trend_change = round((recent_trend - previous_trend) / previous_trend * 100, 1) if previous_trend > 0 else None

        cursor.execute(
            """SELECT COALESCE(SUM(c.co2e), 0) AS previous_month_total
               FROM activities a JOIN carbon_records c ON c.activity_id = a.id
               WHERE a.user_id = %s
                 AND a.activity_date >= DATE_SUB(DATE_SUB(CURDATE(), INTERVAL (DAYOFMONTH(CURDATE()) - 1) DAY), INTERVAL 1 MONTH)
                 AND a.activity_date < DATE_SUB(CURDATE(), INTERVAL (DAYOFMONTH(CURDATE()) - 1) DAY)""",
            (user["id"],),
        )
        previous_month_total = float(cursor.fetchone()["previous_month_total"] or 0)
        reduction = round((previous_month_total - total) / previous_month_total * 100, 1) if previous_month_total > 0 else None

        cursor.execute(
            """SELECT a.category, a.activity_type, CAST(a.activity_date AS CHAR) AS activity_date,
                      ROUND(c.co2e, 3) AS co2e
               FROM activities a JOIN carbon_records c ON c.activity_id = a.id
               WHERE a.user_id = %s ORDER BY a.activity_date DESC, a.id DESC LIMIT 5""",
            (user["id"],),
        )
        recent_activities = cursor.fetchall()

        recommendation = None
        top_category = None
        share = 0.0
        actions = []
        if has_emissions:
            top_category = max(categories, key=categories.get)
            recommendation = RECOMMENDATIONS[top_category]
            share = round(categories[top_category] / total * 100, 1)
            opportunity = recommendation["opportunity"]
            actions = recommendation["actions"]
        elif has_activities:
            opportunity = "Your logged activities have no direct emissions in this estimate. Add other activities to get more tailored guidance."
        else:
            opportunity = "Start tracking your activities to receive personalized sustainability guidance."

        return {
            "largest_contributor": recommendation["name"] if recommendation else None,
            "observation": f"{recommendation['name']} is currently your largest emission category." if recommendation else None,
            "recommendation": recommendation["opportunity"] if recommendation else opportunity,
            "contribution_percent": share,
            "opportunity": opportunity,
            "actions": actions,
            "potential_impact_kg": None,
            "period": "current_month",
            "method": "rule_based",
            "has_activities": has_activities,
            "has_emissions": has_emissions,
            "activity_count": activity_count,
            "total_co2e": round(total, 3),
            "category_totals": categories,
            "recent_activities": recent_activities,
            "monthly_goal": goal_progress,
            "monthly_reduction_percent": reduction,
            "has_monthly_reduction_baseline": previous_month_total > 0,
            "trend_7d": {
                "current_period_co2e": round(recent_trend, 3),
                "previous_period_co2e": round(previous_trend, 3),
                "change_percent": trend_change,
                "has_baseline": previous_trend > 0,
            },
        }
    except Exception as error:
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
