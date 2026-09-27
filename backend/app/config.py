"""Application configuration settings for PlanetPulse."""

import os

# Default monthly carbon emissions target in kg CO2e
DEFAULT_MONTHLY_GOAL_CO2E: float = float(
    os.getenv("DEFAULT_MONTHLY_GOAL_CO2E", "100.0")
)

# Authentication & JWT Configuration
JWT_SECRET_KEY: str = os.getenv(
    "JWT_SECRET_KEY", "planetpulse-dev-secret-key-must-be-at-least-32-chars-long!"
)
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_SECONDS: int = int(os.getenv("JWT_EXPIRATION_SECONDS", "43200"))  # 12 hours

# CORS Configuration
CORS_ORIGINS: str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173,http://localhost:3000,http://127.0.0.1:3000",
)
