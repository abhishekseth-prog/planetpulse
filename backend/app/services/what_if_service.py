from app.carbon.calculator import calculate_co2e
from app.schemas.what_if import WhatIfRequest, WhatIfResponse


def calculate_what_if_simulation(request: WhatIfRequest) -> WhatIfResponse:
    """Simulate carbon footprint comparison between current and alternative scenarios.

    Uses the exact same centralized Carbon Calculation Engine (calculate_co2e).
    """
    current_val = calculate_co2e(
        activity=request.current.activity,
        amount=request.current.amount,
        unit=request.current.unit,
    )
    new_val = calculate_co2e(
        activity=request.alternative.activity,
        amount=request.alternative.amount,
        unit=request.alternative.unit,
    )

    current_co2 = round(current_val, 3)
    new_co2 = round(new_val, 3)
    daily_diff = round(current_co2 - new_co2, 3)
    monthly_diff = round(daily_diff * 30, 3)
    reduction_pct = round((daily_diff / current_co2 * 100), 1) if current_co2 > 0 else 0.0
    is_reduction = daily_diff > 0

    return WhatIfResponse(
        current_co2=current_co2,
        current_kg_co2e=current_co2,
        new_co2=new_co2,
        new_kg_co2e=new_co2,
        daily_reduction=daily_diff,
        saving_kg_per_day=daily_diff,
        monthly_reduction=monthly_diff,
        saving_kg_per_month=monthly_diff,
        reduction_percent=reduction_pct,
        is_reduction=is_reduction,
    )
