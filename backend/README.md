# PlanetPulse — Backend Engine

PlanetPulse converts daily activities (Travel, Electricity, Food) into estimated personal carbon emissions (CO2e).

This repository contains the backend service responsible for data validation, emission calculations, persistence, aggregation, goal tracking, and what-if comparative analysis.

---

## Architecture & Folder Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entrypoint with lifespan DB initialization
│   ├── routes/              # API route definitions
│   │   ├── health.py        # Health check router (GET /api/health)
│   │   ├── activities.py    # Activity ingestion router (POST /api/activities)
│   │   ├── dashboard.py     # Dashboard summary router (GET /api/dashboard)
│   │   └── trend.py         # Time-series trend router (GET /api/trend)
│   ├── controllers/         # Request handling & orchestration
│   ├── services/            # Business & domain services
│   │   ├── activity_service.py  # Carbon calculation and activity persistence
│   │   ├── dashboard_service.py # Database-side aggregation for dashboard metrics
│   │   └── trend_service.py     # Database-side time-series trend aggregation
│   ├── models/              # SQLAlchemy database models
│   │   └── activity.py      # Activity ORM model with co2e column
│   ├── schemas/             # Pydantic schemas for request/response validation
│   │   ├── activity.py      # ActivityBase, ActivityCreate, ActivityResponse
│   │   ├── dashboard.py     # CategorySummary, DashboardCategories, DashboardResponse
│   │   └── trend.py         # TrendPoint, TrendResponse
│   ├── database/            # Database engine, session, and base definitions
│   │   └── session.py       # SQLite connection, SessionLocal, get_db, init_db
│   └── carbon/              # Centralized Carbon Calculation Engine (Stage 3)
│       ├── factors.py       # Centralized emission factors repository
│       ├── calculator.py    # calculate_co2e calculation service
│       └── exceptions.py    # Domain-specific calculation exceptions
├── tests/                   # Pytest test suite
│   ├── conftest.py          # Shared test database fixtures
│   ├── test_health.py       # Health check test
│   ├── test_activity_schema_and_db.py  # Schema validation and database tests
│   ├── test_carbon_engine.py           # Carbon Engine calculation tests
│   ├── test_activities_api.py          # POST /api/activities integration tests
│   ├── test_dashboard_api.py           # GET /api/dashboard integration tests
│   └── test_trend_api.py               # GET /api/trend integration tests
├── requirements.txt         # Production and development dependencies
├── .env.example             # Safe environment variable template
├── README.md                # Documentation and setup guide
└── DECISIONS.md             # Technical and architectural decisions
```

---

## Setup & Installation

### Prerequisites

* Python 3.10+ (tested on Python 3.13)
* `pip` package manager

### 1. Clone & Navigate to Backend

```bash
cd backend
```

### 2. Create and Activate Virtual Environment (Optional but recommended)

```bash
python -m venv .venv

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

---

## Running the Server

Start the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

* API Docs (Swagger UI): `http://127.0.0.1:8001/docs`
* ReDoc: `http://127.0.0.1:8001/redoc`

---

## API Endpoints

### 1. Health Check

* **Endpoint**: `GET /api/health`
* **Description**: Verifies backend application liveness.
* **Request**: None
* **Response**:
  ```json
  {
    "status": "ok"
  }
  ```

### 2. Record Activity (Stage 4)

* **Endpoint**: `POST /api/activities`
* **Status Code**: `201 Created`
* **Description**: Validates activity payload, computes personal emissions via the centralized Carbon Engine, saves the activity to the database, and returns the persisted record with calculated CO2e.
* **Request Example**:
  ```json
  {
    "category": "travel",
    "activity": "car",
    "amount": 20,
    "unit": "km",
    "date": "2026-09-27"
  }
  ```
* **Response Example**:
  ```json
  {
    "id": 1,
    "category": "travel",
    "activity": "car",
    "amount": 20.0,
    "unit": "km",
    "date": "2026-09-27",
    "co2e": 4.2,
    "created_at": "2026-09-27T08:11:21.449893"
  }
  ```
* **Validation Behavior**:
  * Returns `422 Unprocessable Entity` for missing fields, non-positive amounts, invalid categories, unsupported units, or malformed calendar dates.
  * Validation failure guarantees that no database record is persisted.

### 3. Dashboard Overview & Category Breakdown (Stage 5)

* **Endpoint**: `GET /api/dashboard`
* **Status Code**: `200 OK`
* **Description**: Aggregates total emissions and categorical breakdowns (`travel`, `electricity`, `food`) directly from the database using SQL aggregations. Does **not** recalculate emissions.
* **Query Parameters (Optional)**:
  * `start_date` (`YYYY-MM-DD`): Filters activities occurring on or after this date.
  * `end_date` (`YYYY-MM-DD`): Filters activities occurring on or before this date.
  * *Validation*: If `start_date > end_date`, returns `422 Unprocessable Entity`.
* **Response Example**:
  ```json
  {
    "total_co2": 9.575,
    "total_activities": 3,
    "categories": {
      "travel": {
        "co2e": 4.2,
        "activities": 1
      },
      "electricity": {
        "co2e": 3.375,
        "activities": 1
      },
      "food": {
        "co2e": 2.0,
        "activities": 1
      }
    }
  }
  ```
* **Empty Database Behavior**:
  If no activities exist, returns `total_co2: 0.0`, `total_activities: 0`, and all categories initialized to `{"co2e": 0.0, "activities": 0}` (never `null`).

### 4. Emissions Trend (Stage 6)

* **Endpoint**: `GET /api/trend`
* **Status Code**: `200 OK`
* **Description**: Returns daily aggregated carbon emissions and activity counts sorted in ascending chronological order. Aggregates stored `co2e` values directly at the database level.
* **Query Parameters (Optional)**:
  * `start_date` (`YYYY-MM-DD`): Filters activities occurring on or after this date.
  * `end_date` (`YYYY-MM-DD`): Filters activities occurring on or before this date.
  * *Validation*: If `start_date > end_date`, returns `422 Unprocessable Entity`.
* **Response Example**:
  ```json
  {
    "trend": [
      {
        "date": "2026-09-10",
        "co2e": 4.2,
        "activities": 1
      },
      {
        "date": "2026-09-20",
        "co2e": 3.375,
        "activities": 1
      },
      {
        "date": "2026-09-27",
        "co2e": 9.375,
        "activities": 3
      }
    ]
  }
  ```
* **Same-Day Aggregation**: Multiple activities occurring on the same date are consolidated into a single trend point.
* **Empty Database Behavior**: Returns `{"trend": []}` when no matching activities are found.

---

## Activity Data Model & Database

### Database Configuration

* **Engine**: SQLite via SQLAlchemy 2.0 (`sqlite:///./planetpulse.db`).
* **Table**: `activities`
* **Columns**:
  * `id`: `INTEGER` (Primary Key, auto-increment)
  * `category`: `VARCHAR(50)` (Indexed, non-null)
  * `activity`: `VARCHAR(100)` (Non-null)
  * `amount`: `FLOAT` (Non-null, must be > 0)
  * `unit`: `VARCHAR(20)` (Non-null)
  * `date`: `DATE` (Indexed, non-null)
  * `co2e`: `FLOAT` (Non-null, calculated emissions in kg CO2e)
  * `created_at`: `DATETIME` (UTC timestamp, non-null)

---

## Centralized Carbon Calculation Engine

The Carbon Calculation Engine (`app/carbon/`) is the single source of truth for carbon calculations across the system:

```text
Activity (activity, amount, unit)
       ↓
find_factor(activity, unit)
       ↓
CO2e = amount × emission_factor (kg CO2e)
```

* **Core Function**: `calculate_co2e(activity: str, amount: float, unit: str) -> float`
* **Zero Duplication**: Emission factors are maintained strictly inside `app/carbon/factors.py` and never hardcoded in routes or database code.

---

## Running Tests

Execute the complete test suite using `pytest`:

```bash
pytest -v
```
