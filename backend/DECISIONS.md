# PlanetPulse Backend — Architectural & Technical Decisions

This document records the architectural, algorithmic, and data decisions made across the lifecycle of the PlanetPulse backend.

---

## 1. Architectural Decisions

* **Framework**: FastAPI was chosen for its high-performance asynchronous execution, native OpenAPI/Swagger generation, and tight integration with Pydantic for robust request validation and typed contracts.
* **Database & ORM**: SQLite + SQLAlchemy 2.0.
  * **Why SQLite + SQLAlchemy Was Retained**: SQLite provides zero-configuration, reliable file-based persistence without requiring an external MySQL daemon or host setup. SQLAlchemy 2.0 ORM provides strict type safety, clean data model encapsulation, and effortless portability should production migration to PostgreSQL or MySQL be desired in the future.
  * **Why Raw MySQL Code Was Not Copied**: Copying raw `mysql-connector-python` scripts with hardcoded MySQL syntax would break SQLite portability, erase test suite isolation, and discard the verified SQLAlchemy ORM architecture built in Stages 1–7.
* **Separation of Concerns**:
  * `routes/`: Define API contracts, HTTP methods, and URL prefixes. Mounted under both `/api/...` and root `/...` for complete frontend compatibility.
  * `schemas/`: Pydantic v2 validation for incoming payloads, alias normalizations, and response serialization.
  * `models/`: SQLAlchemy database entity definitions (`Activity`, `User`, `UserGoal`).
  * `carbon/`: Centralized emission factors (`factors.py`) and pure calculation engine (`calculator.py`). Never mixed into route handlers.
  * `services/`: Encapsulates business logic (aggregations, goal tracking, auth management, what-if projections, insights).
  * `database/`: Database connection pooling and session lifecycle management (`get_db`).

---

## 2. Ingestion Pipeline & Persistence of Calculated CO2e

* **Addition of `co2e` Column to `Activity` Model**: In Stage 4, `co2e = Column(Float, nullable=False, default=0.0)` was added to the `activities` table.
* **Rationale**:
  1. **Query Performance**: Storing calculated emissions at ingestion allows direct indexed database aggregations without dynamically re-evaluating calculations on every read.
  2. **Historical Immutability**: If emission factors are updated in the future, past user activities retain their emissions as calculated at the time of recording.
  3. **Zero Duplication**: The value stored is calculated strictly by calling `calculate_co2e(...)` from `app.carbon.calculator`. No emission formulas or factor numbers are duplicated inside routes or services.

---

## 3. Carbon Engine & Emission Factor Decisions

### Why Centralize Factors?
1. **Single Source of Truth**: All components calculating greenhouse gas emissions (`POST /api/activities`, What-If Simulation Engine) query the exact same factor registry.
2. **Auditability & Traceability**: Centralization allows transparent attribution of every factor to an authoritative source or explicit assumption.
3. **Prevent Divergence**: Scattering formulas across endpoints causes subtle rounding errors and inconsistent user-facing carbon metrics.

### Factor Registry & Aliasing
Emission factors are modeled as immutable `EmissionFactor` dataclasses in `app/carbon/factors.py`. To ensure seamless compatibility with different frontend and historical representations, input normalizations map common synonyms (e.g. `air conditioner` → `ac`, `chicken meal` → `chicken_meal`, `plant-based meal` → `vegan_meal`, `dairy meal` → `dairy`, `appliance` → `appliances`).

#### Travel (Base unit: km; 1 mile = 1.60934 km)
* **Car**: `0.21 kg CO2e/km` (0.33796 kg CO2e/mile) — *Source*: UK DEFRA / DESNZ GHG Conversion Factors (Average petrol passenger car).
* **Bus**: `0.10 kg CO2e/km` (0.16093 kg CO2e/mile) — *Source*: UK DEFRA / DESNZ GHG Conversion Factors (Average local bus).
* **Train**: `0.04 kg CO2e/km` (0.06437 kg CO2e/mile) — *Source*: UK DEFRA / DESNZ GHG Conversion Factors (National / regional rail).
* **Metro**: `0.03 kg CO2e/km` (0.04828 kg CO2e/mile) — *Source*: UK DEFRA / DESNZ GHG Conversion Factors (Light rail and metro transit).
* **Flight / Plane**: `0.25 kg CO2e/km` (0.40234 kg CO2e/mile) — *Source*: UK DEFRA / DESNZ GHG Conversion Factors (Domestic/short-haul flight).
* **Motorcycle**: `0.11 kg CO2e/km` (0.17703 kg CO2e/mile) — *Source*: UK DEFRA / DESNZ GHG Conversion Factors (Medium motorbike).
* **Bike / Walk**: `0.0 kg CO2e/km` — *Source*: Direct tailpipe emission standard (human powered).

#### Electricity (Base grid intensity: 0.45 kg CO2e/kWh)
* **Source**: International Energy Agency (IEA) global average grid carbon intensity (~0.45 kg CO2e/kWh).
* **Direct Consumption (`kwh`)**: All electricity activities measured in `kwh` use `0.45 kg CO2e/kWh`.
* **Hours-based Consumption (`hours`)**: `Power Rating (kW) × 0.45 kg CO2e/kWh`.
  * **AC**: `1.5 kW × 0.45 = 0.675 kg CO2e/hour` (1.5-ton split AC).
  * **Fan**: `0.06 kW × 0.45 = 0.027 kg CO2e/hour` (60W standard fan).
  * **Heater**: `1.5 kW × 0.45 = 0.675 kg CO2e/hour` (1500W electric space heater).
  * **Lighting**: `0.03 kW × 0.45 = 0.0135 kg CO2e/hour` (30W active LED/CFL).
  * **Refrigerator**: `0.10 kW × 0.45 = 0.045 kg CO2e/hour` (100W compressor average).
  * **Computer**: `0.15 kW × 0.45 = 0.0675 kg CO2e/hour` (150W active computing load).
  * **TV**: `0.10 kW × 0.45 = 0.045 kg CO2e/hour` (100W television).
  * **Appliances**: `0.50 kW × 0.45 = 0.225 kg CO2e/hour` (500W aggregate appliances).

#### Food (References: Poore & Nemecek 2018, Science; Our World in Data)
* **Chicken Meal**: `1.8 kg CO2e/meal` (`7.0 kg CO2e/kg`)
* **Beef Meal**: `6.5 kg CO2e/meal` (`60.0 kg CO2e/kg`)
* **Fish Meal**: `1.4 kg CO2e/meal` (`5.5 kg CO2e/kg`)
* **Vegetarian Meal**: `0.8 kg CO2e/meal` (`3.0 kg CO2e/kg`)
* **Vegan Meal**: `0.5 kg CO2e/meal` (`2.0 kg CO2e/kg`)
* **Dairy**: `0.6 kg CO2e/meal` (`3.5 kg CO2e/kg`)

---

## 4. What-If Carbon Simulation Engine

* **Centralized Engine Calling**: `POST /api/what-if` invokes `calculate_co2e(...)` for both current and alternative scenarios.
* **Calculation Metrics**:
  * `daily_reduction = round(current_co2 - new_co2, 3)`
  * `monthly_reduction = round(daily_reduction * 30, 3)` (Standard 30-day screening projection)
  * `reduction_percent = round((daily_reduction / current_co2 * 100), 1)`
  * `is_reduction = (daily_reduction > 0)`

---

## 5. Authentication, JWT & Multi-Tenant User Scoping

* **Password Security**: Standard library `hashlib.scrypt` with 16-byte cryptographically random salt (`scrypt$<salt_hex>$<digest_hex>`), impervious to rainbow tables and hardware-accelerated dictionary attacks.
* **Token Verification**: Signed `HS256` HMAC-SHA256 JWT tokens with 12-hour validity.
* **Multi-Tenant User Isolation**:
  * Activities, user monthly goals, dashboard statistics, trends, and recommendations are strictly scoped by `user_id` when authenticated.
  * User A cannot access, view, or alter User B's activities or goals.
  * Anonymous / local single-user mode is preserved for developer velocity and backward compatibility.

---

## 6. Monthly Goals & Target Customization

* **Dynamic Goal Targets**: Stored in `user_goals` table per user and calendar month (`YYYY-MM`).
* **Defaults**: Defaults to 100.0 kg CO2e if no custom target is set.
* **Dual Endpoint Support**: Supports both legacy `GET /api/goal` (with `month`/`year` parameters) and team contract `GET /api/goals/monthly` & `PUT /api/goals/monthly`.

---

## 7. Deterministic AI / Rule-Based Insights

* **Rule-Based Architecture**: Avoids fragile external LLM dependencies for critical core reporting.
* **Methodology**: Evaluates the user's top carbon emitting category in the current month and calculates the potential savings of a targeted 10% reduction, returning specific, actionable behavioral changes.

---

## 8. CORS & Route Compatibility

* **CORS**: Configurable via `CORS_ORIGINS` environment variable, defaulting to `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:4173`, `http://127.0.0.1:4173`.
* **Dual Routing**: All routers are registered at `/` and with the `/api` prefix to satisfy all frontend configurations without URL mismatch friction.
