from fastapi import APIRouter, HTTPException, status
from app.schemas.what_if import WhatIfRequest, WhatIfResponse
from app.services.what_if_service import calculate_what_if_simulation
from app.carbon.exceptions import CarbonEngineError

router = APIRouter(tags=["what-if"])


@router.post(
    "/what-if",
    response_model=WhatIfResponse,
    summary="Simulate carbon emission reductions between two scenarios",
)
def simulate_what_if(payload: WhatIfRequest):
    """Run what-if scenario comparison using the centralized carbon engine."""
    try:
        return calculate_what_if_simulation(payload)
    except CarbonEngineError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
