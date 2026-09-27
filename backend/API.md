# PlanetPulse API Specification & Contract

Base URL for local development: `http://127.0.0.1:8001`.
Interactive Swagger UI is available at `http://127.0.0.1:8001/docs`.
Interactive ReDoc is available at `http://127.0.0.1:8001/redoc`.

All endpoints are available at `/api/...` (standard team contract) and at root paths `/...` (for frontend backward compatibility).

---

## 1. Health & Status

### `GET /api/health` and `GET /health`
Verify backend service and database availability.

- **Authentication**: None (Public)
- **Response** `200 OK`:
  ```json
  {
    "status": "ok"
  }
  ```

### `GET /`
Service entry point.

- **Authentication**: None (Public)
- **Response** `200 OK`:
  ```json
  {
    "message": "PlanetPulse API is running",
    "status": "ok",
    "health": "/api/health",
    "docs": "/docs"
  }
  ```

---

## 2. Authentication

Authentication uses salted `scrypt` password hashing and signed `HS256` JWT access tokens with 12-hour validity.

### `POST /api/auth/register`
Register a new user account.

- **Authentication**: None (Public)
- **Request Body**:
  ```json
  {
    "name": "Asha Yadav",
    "email": "asha@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Validation**:
  - `name`: String, 2–100 characters.
  - `email`: Valid RFC 5322 email string. Duplicate email returns `409 Conflict`.
  - `password`: String, 10–128 characters.
- **Response** `201 Created`:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "Asha Yadav",
      "email": "asha@example.com"
    }
  }
  ```

### `POST /api/auth/login`
Authenticate with email and password.

- **Authentication**: None (Public)
- **Request Body**:
  ```json
  {
    "email": "asha@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Validation**:
  - Invalid credentials return `401 Unauthorized`.
- **Response** `200 OK`:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "Asha Yadav",
      "email": "asha@example.com"
    }
  }
  ```

### `GET /api/auth/me`
Retrieve authenticated user profile.

- **Authentication**: Required (`Authorization: Bearer <access_token>`)
- **Response** `200 OK`:
  ```json
  {
    "id": 1,
    "name": "Asha Yadav",
    "email": "asha@example.com"
  }
  ```

---

## 3. Activities

### `POST /api/activities`
Log a daily activity and calculate estimated CO2e emissions using the centralized Carbon Engine.

- **Authentication**: Optional. If authenticated, activity is associated with the user account; otherwise saved anonymously.
- **Request Body** (Canonical format or frontend aliases):
  ```json
  {
    "category": "travel",
    "activity": "car",
    "amount": 20,
    "unit": "km",
    "date": "2026-09-27"
  }
  ```
  *Frontend compatibility aliases supported*:
  - `activity_type` in place of `activity`
  - `value` in place of `amount`
  - `activity_date` in place of `date`
- **Supported Categories & Units**:
  - `travel`: `car`, `bus`, `train`, `metro`, `flight`, `bike`, `walk`, `motorcycle` (`km`, `miles`)
  - `electricity`: `ac`, `fan`, `heater`, `lighting`, `refrigerator`, `computer`, `tv`, `appliances` (`hours`, `kwh`)
  - `food`: `chicken_meal`, `beef_meal`, `vegetarian_meal`, `vegan_meal`, `fish_meal`, `dairy` (`meal`, `servings`, `kg`)
- **Response** `201 Created`:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "category": "travel",
    "activity": "car",
    "activity_type": "car",
    "amount": 20.0,
    "value": 20.0,
    "unit": "km",
    "date": "2026-09-27",
    "activity_date": "2026-09-27",
    "co2e": 4.2,
    "carbon_kg_co2e": 4.2,
    "created_at": "2026-09-27T10:00:00Z"
  }
  ```

### `GET /api/activities`
Retrieve recorded activity history with optional filtering.

- **Authentication**: Optional (scoped to authenticated user if bearer token is provided).
- **Query Parameters**:
  - `category` (optional): `travel`, `electricity`, `food`
  - `start_date` (optional): `YYYY-MM-DD`
  - `end_date` (optional): `YYYY-MM-DD`
- **Response** `200 OK`:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "category": "travel",
      "activity": "car",
      "amount": 20.0,
      "unit": "km",
      "date": "2026-09-27",
      "co2e": 4.2,
      "created_at": "2026-09-27T10:00:00Z"
    }
  ]
  ```

---

## 4. Dashboard

### `GET /api/dashboard`
Aggregated emissions totals, category breakdowns, month-over-month reduction, and goal progress.

- **Authentication**: Optional (scoped to user when authenticated).
- **Query Parameters**:
  - `start_date` (optional): `YYYY-MM-DD`
  - `end_date` (optional): `YYYY-MM-DD`
- **Response** `200 OK`:
  ```json
  {
    "total_co2": 27.2,
    "total_co2e": 27.2,
    "total_activities": 11,
    "activities": 11,
    "travel": 21.6,
    "travel_co2e": 21.6,
    "electricity": 4.6,
    "electricity_co2e": 4.6,
    "food": 1.0,
    "food_co2e": 1.0,
    "reduction": 12.4,
    "reduction_percent": 12.4,
    "goal": {
      "target": 100.0,
      "current": 27.2,
      "progress": 27.2,
      "remaining": 72.8
    },
    "goal_progress": {
      "target_co2e": 100.0,
      "used_co2e": 27.2,
      "progress_percent": 27.2,
      "remaining_co2e": 72.8
    },
    "categories": {
      "travel": { "co2e": 21.6, "activities": 5 },
      "electricity": { "co2e": 4.6, "activities": 4 },
      "food": { "co2e": 1.0, "activities": 2 }
    }
  }
  ```

---

## 5. Trend

### `GET /api/trend`
Chronological daily emissions data.

- **Authentication**: Optional (scoped to user when authenticated).
- **Query Parameters**:
  - `period` (optional): `7d`, `30d`, `3m` (returns zero-filled consecutive daily points).
  - `start_date` (optional): `YYYY-MM-DD`
  - `end_date` (optional): `YYYY-MM-DD`
- **Response** `200 OK` (when `period` specified):
  ```json
  [
    { "date": "2026-09-21", "label": "Mon", "co2e": 0.0 },
    { "date": "2026-09-22", "label": "Tue", "co2e": 4.2 },
    { "date": "2026-09-23", "label": "Wed", "co2e": 1.8 },
    { "date": "2026-09-24", "label": "Thu", "co2e": 0.0 },
    { "date": "2026-09-25", "label": "Fri", "co2e": 3.1 },
    { "date": "2026-09-26", "label": "Sat", "co2e": 0.0 },
    { "date": "2026-09-27", "label": "Sun", "co2e": 5.2 }
  ]
  ```
- **Response** `200 OK` (default):
  ```json
  {
    "trend": [
      { "date": "2026-09-22", "co2e": 4.2, "activities": 1 },
      { "date": "2026-09-27", "co2e": 5.2, "activities": 2 }
    ]
  }
  ```

---

## 6. Monthly Goals

### `GET /api/goals/monthly` and `GET /api/goal`
Retrieve current monthly carbon budget target and actual progress.

- **Authentication**: Optional (scoped to user when authenticated).
- **Query Parameters** for `/api/goals/monthly`:
  - `month` (optional): `YYYY-MM`
- **Response** `200 OK`:
  ```json
  {
    "target": 100.0,
    "current": 27.2,
    "progress": 27.2,
    "remaining": 72.8,
    "target_co2e": 100.0,
    "used_co2e": 27.2,
    "progress_percent": 27.2,
    "remaining_co2e": 72.8,
    "month": "2026-09"
  }
  ```

### `PUT /api/goals/monthly`
Update the monthly carbon reduction target.

- **Authentication**: Optional (persisted for authenticated user or anonymous session).
- **Request Body**:
  ```json
  {
    "target": 120.0
  }
  ```
  *(Also accepts `target_kg` or `target_co2e`)*
- **Validation**: `target` must be between `1.0` and `100000.0` kg CO2e.
- **Response** `200 OK`:
  ```json
  {
    "target": 120.0,
    "current": 27.2,
    "progress": 22.7,
    "remaining": 92.8,
    "target_co2e": 120.0,
    "used_co2e": 27.2,
    "progress_percent": 22.7,
    "remaining_co2e": 92.8,
    "month": "2026-09"
  }
  ```

---

## 7. What-If Carbon Simulation

### `POST /api/what-if`
Simulate and compare carbon footprint differences between current activity and a lower-carbon alternative using the centralized calculation engine.

- **Authentication**: None (Public)
- **Request Body** (supports nested or flat contract):
  ```json
  {
    "current": {
      "activity": "car",
      "amount": 20,
      "unit": "km"
    },
    "alternative": {
      "activity": "metro",
      "amount": 20,
      "unit": "km"
    }
  }
  ```
  *Or flat format:*
  ```json
  {
    "category": "travel",
    "current_activity": "car",
    "alternative_activity": "metro",
    "distance": 20,
    "unit": "km"
  }
  ```
- **Response** `200 OK`:
  ```json
  {
    "current_co2": 4.2,
    "current_kg_co2e": 4.2,
    "new_co2": 0.6,
    "new_kg_co2e": 0.6,
    "daily_reduction": 3.6,
    "saving_kg_per_day": 3.6,
    "monthly_reduction": 108.0,
    "saving_kg_per_month": 108.0,
    "reduction_percent": 85.7,
    "is_reduction": true
  }
  ```

---

## 8. AI & Rule-Based Insights

### `GET /api/insights`
Retrieve personalized, actionable carbon reduction recommendations derived deterministically from the user's current month activities.

- **Authentication**: Optional (scoped to user when authenticated).
- **Response** `200 OK`:
  ```json
  {
    "largest_contributor": "Travel",
    "contribution_percent": 79.4,
    "opportunity": "Replacing short car trips with public transit or active travel is your clearest opportunity. A 10% reduction in travel could avoid about 2.2 kg CO2e this month.",
    "actions": [
      "Replace 2 short car trips with metro, bus, or cycling",
      "Combine nearby errands into a single journey",
      "Choose a lower-impact commute option once this week"
    ],
    "potential_impact_kg": 2.2,
    "period": "current_month",
    "method": "rule_based"
  }
  ```
