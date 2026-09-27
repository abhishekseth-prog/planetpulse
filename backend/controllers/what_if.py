from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, root_validator

from services.calculator import calculate_carbon
from controllers.common import get_current_user

router = APIRouter()


class Scenario(BaseModel):
    activity: str
    amount: float
    unit: str = "km"


class WhatIfRequest(BaseModel):
    current: Scenario | None = None
    alternative: Scenario | None = None
    category: str = "travel"
    current_activity: str | None = None
    alternative_activity: str | None = None
    distance: float | None = None
    unit: str = "km"

    @root_validator(pre=True)
    def normalize_frontend_contract(cls, values):
        values = dict(values or {})
        amount = values.get("distance", 20)
        unit = values.get("unit", "km")
        if "current" not in values and values.get("current_activity"):
            values["current"] = {"activity": values["current_activity"], "amount": amount, "unit": unit}
        if "alternative" not in values and values.get("alternative_activity"):
            values["alternative"] = {"activity": values["alternative_activity"], "amount": amount, "unit": unit}
        return values


@router.post("/what-if")
def simulate(payload: WhatIfRequest, user=Depends(get_current_user)):
    if payload.current is None or payload.alternative is None:
        raise HTTPException(status_code=422, detail="current and alternative scenarios are required")
    try:
        current = calculate_carbon(payload.category, payload.current.amount, payload.current.activity, payload.current.unit)
        new = calculate_carbon(payload.category, payload.alternative.amount, payload.alternative.activity, payload.alternative.unit)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    saved = round(current - new, 3)
    return {
        "current_co2": current, "current_kg_co2e": current,
        "new_co2": new, "new_kg_co2e": new,
        "daily_reduction": saved, "saving_kg_per_day": saved,
        "monthly_reduction": round(saved * 30, 3), "saving_kg_per_month": round(saved * 30, 3),
        "reduction_percent": round(saved / current * 100, 1) if current else 0,
    }
