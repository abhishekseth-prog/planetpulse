from fastapi import APIRouter, Depends

from controllers.common import database_error
from controllers.dashboard import monthly_totals
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
        top_category = max(categories, key=categories.get)
        top_value = categories[top_category]
        recommendation = RECOMMENDATIONS[top_category]
        share = round(top_value / total * 100, 1) if total else 0.0

        if total:
            potential = round(top_value * 0.10, 1)
            opportunity = (
                f"{recommendation['opportunity']} A 10% reduction in {recommendation['name'].lower()} "
                f"could avoid about {potential:g} kg CO₂e this month."
            )
        else:
            potential = 0.0
            opportunity = "Start logging activities to get recommendations based on your footprint."

        return {
            "largest_contributor": recommendation["name"],
            "contribution_percent": share,
            "opportunity": opportunity,
            "actions": recommendation["actions"],
            "potential_impact_kg": potential,
            "period": "current_month",
            "method": "rule_based",
        }
    except Exception as error:
        raise database_error(error) from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
