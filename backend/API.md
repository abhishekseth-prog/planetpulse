# PlanetPulse API contract

Base URL for local development: `http://127.0.0.1:8001`. Every endpoint below is available both at the listed path and with the `/api` prefix. JSON errors use FastAPI's standard `{ "detail": "..." }` response.

## Start locally

From the `backend` directory, install `requirements.txt`, copy `.env.example` to `.env`, set the MySQL password, and replace `JWT_SECRET_KEY` with at least 32 random bytes. For a fresh database, run `schema.sql`; to preserve an existing activity database, run `python migrate_auth.py` once. Start with `uvicorn main:app --reload --port 8001`. Swagger docs are available at `/docs`.

## Authentication

`POST /api/auth/register` accepts `{ "name":"Asha Yadav", "email":"asha@example.com", "password":"at-least-10-characters" }` and returns a bearer access token and public user object. Registration validates email and password and rejects duplicate email addresses. Passwords are stored as salted scrypt hashes.

`POST /api/auth/login` accepts `{ "email":"asha@example.com", "password":"..." }` and returns `{ "access_token":"...", "token_type":"bearer", "user":{"id":1,"name":"Asha Yadav","email":"asha@example.com"} }`.

Pass `Authorization: Bearer <access_token>` for all private routes. Tokens expire after 12 hours. `GET /api/auth/me` returns the authenticated user's public profile. `GET /api/health` remains public. Legacy activity rows keep their existing user IDs under disabled legacy accounts during migration and are never shown to newly registered users.

## Health

`GET /api/health` → `{ "status": "ok" }`

## Create and list activities

`POST /api/activities` (201)

Canonical request:

```json
{
  "category": "travel",
  "activity": "car",
  "amount": 20,
  "unit": "km",
  "date": "2026-09-27"
}
```

`activity`/`amount`/`date` are also accepted as the existing frontend aliases `activity_type`/`value`/`activity_date`. Categories are `travel`, `electricity`, `food`. Units: travel `km`, electricity `kWh` (or appliance `hours`, maximum 24/day), food `meal`. Travel modes: `car`, `metro`, `bus`, `bike`, `walk`. Electricity activity names include `Air conditioner`, `Lighting`, `Refrigerator`, and `Other appliance`. Food types include `Plant-based meal`, `Chicken meal`, `Dairy meal`, and `Beef meal`.

```json
{
  "id": 12,
  "activity_id": 12,
  "category": "travel",
  "activity": "car",
  "activity_type": "car",
  "amount": 20,
  "value": 20,
  "unit": "km",
  "date": "2026-09-27",
  "activity_date": "2026-09-27",
  "co2e": 5.8,
  "carbon_kg_co2e": 5.8
}
```

`GET /api/activities` returns an array with both canonical and existing frontend field names.

All activity routes require a valid bearer token; `user_id` is always derived from that token and is never accepted from the request body. Positive finite amounts are required. Dates must be ISO `YYYY-MM-DD`; units, category, and activity must match the central factor configuration. Invalid inputs receive HTTP 422.

## Dashboard

`GET /api/dashboard` returns the current calendar month's totals, category values, activity count, month-over-month reduction, and goal progress:

```json
{
  "total_co2": 27.2,
  "total_co2e": 27.2,
  "travel": 21.6,
  "travel_co2e": 21.6,
  "electricity": 4.6,
  "electricity_co2e": 4.6,
  "food": 1.0,
  "food_co2e": 1.0,
  "activities": 11,
  "total_activities": 11,
  "reduction": 12.4,
  "reduction_percent": 12.4,
  "has_previous_month_data": true,
  "current_month": { "start": "2026-09-01", "through": "2026-09-27", "label": "September 2026", "period": "month_to_date", "total_co2e": 27.2 },
  "previous_month": { "start": "2026-08-01", "through": "2026-08-31", "label": "August 2026", "total_co2e": 31.1, "has_data": true, "categories": { "travel": 21.0, "electricity": 7.1, "food": 3.0 } },
  "goal": { "target": 100, "current": 27.2, "progress": 27.2, "remaining": 72.8 },
  "goal_progress": { "target_co2e": 100, "used_co2e": 27.2, "progress_percent": 27.2, "remaining_co2e": 72.8 }
}
```

Month-over-month reduction is `(previous month - current month-to-date) / previous month * 100`. When there is no previous-month emission baseline, `reduction` and `reduction_percent` are `null`; `has_previous_month_data` is false and the UI shows an empty state instead of inventing a comparison. Period boundaries and previous category totals are returned with the response. Every query is scoped to the bearer token's user.

## Trend

`GET /api/trend?period=7d|30d|3m` returns one point per date in the requested period: `[{"date":"2026-09-27","label":"Sun","co2e":5.2}]`. Days without activity are returned with zero emissions.

## Monthly goal

`GET /api/goals/monthly` returns `{ "target": 100, "current": 27.2, "progress": 27.2, "remaining": 72.8 }` with canonical CO2e aliases. `PUT /api/goals/monthly` accepts `{ "target": 100 }` and returns the updated progress. Goal targets are stored by user and calendar month in `user_goals`; the table is created on first goal request.

## What-if

`POST /api/what-if` accepts either the shared nested contract:

```json
{
  "current": { "activity": "car", "amount": 20, "unit": "km" },
  "alternative": { "activity": "metro", "amount": 20, "unit": "km" }
}
```

or the existing frontend shape `{ "category":"travel", "current_activity":"Car", "alternative_activity":"Metro", "distance":20, "unit":"km" }`.

Response: `{ "current_co2":5.8, "current_kg_co2e":5.8, "new_co2":2.1, "new_kg_co2e":2.1, "daily_reduction":3.7, "saving_kg_per_day":3.7, "monthly_reduction":111, "saving_kg_per_month":111, "reduction_percent":63.8 }`.

What-if uses the exact same `calculate_carbon` service as activity creation. The 30-day value is a projection (`daily reduction × 30`), not a forecast from observed future activity.

## AI insights

`GET /api/insights` returns authenticated, rule-based guidance derived from the account's current-month totals, category emissions, monthly goal, previous-month baseline, recent seven-day trend, and five most recent activities. It returns `observation`, `recommendation`, category totals, goal/trend details, and the recent activity context. It does not return a modeled potential-savings value; numerical savings are only available from the What-if calculation endpoint. Empty accounts receive no category recommendation or actions.
