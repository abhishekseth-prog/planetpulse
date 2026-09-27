from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Health check endpoint to verify backend service status."""
    return {"status": "ok"}
