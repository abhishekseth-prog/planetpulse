# 🌍 PlanetPulse

**Personal Carbon Footprint & Impact Decision Platform**

PlanetPulse is a web-based platform that helps users understand and track the carbon impact of their everyday activities such as **travel, food, and electricity**.

The platform converts activity data into estimated **CO₂e emissions**, provides dashboards and trends, supports monthly carbon goals, and allows users to explore the potential impact of changing their daily choices.

---

## 🚀 Key Features

### 🔐 User Authentication

* User registration and login
* Secure password hashing
* JWT-based authentication
* Protected user-specific APIs
* `/auth/me` endpoint for authenticated user information

### 🌱 Carbon Footprint Tracking

Users can record activities across multiple categories:

* 🚗 Travel
* 🍽️ Food
* ⚡ Electricity

Each activity is processed through a centralized carbon calculation engine to estimate its CO₂e impact.

### 📊 Dashboard

The dashboard provides:

* Total carbon emissions
* Category-wise emissions
* Monthly comparison
* Reduction percentage
* Monthly goal progress
* Activity-based insights

### 📈 Emission Trends

Users can analyze their emissions over different periods:

* Last 7 days
* Last 30 days
* Last 3 months
* Custom date ranges

The trend API also provides zero-filled dates where no activity was recorded, making the frontend charts consistent.

### 🎯 Monthly Carbon Goals

Users can:

* Set a monthly CO₂e target
* View their current goal
* Track progress toward the target

### 🔄 What-If Analysis

PlanetPulse allows users to explore hypothetical changes to their activities and see the estimated difference in CO₂e emissions.

### 💡 Smart Insights

The platform generates deterministic, rule-based insights based on the user's activity and emission patterns.

### 🗄️ Database

The backend uses:

* SQLite
* SQLAlchemy 2.0
* User-scoped data models
* Database migrations with Alembic

---

## 🏗️ System Architecture

```text
                    PLANETPULSE
                        │
          ┌─────────────┴─────────────┐
          │                           │
      Frontend                    Backend
          │                           │
     React / Vite                FastAPI
          │                           │
       Axios                 Service Layer
          │                           │
          └──────────────┬────────────┘
                         │
                  Carbon Engine
                         │
                    SQLAlchemy
                         │
                      SQLite
```

---

## 🛠️ Technology Stack

### Frontend

* React
* Vite
* JavaScript
* Axios
* CSS

### Backend

* Python
* FastAPI
* SQLAlchemy 2.0
* Pydantic
* JWT Authentication
* Alembic

### Database

* SQLite

### Development & Testing

* Git
* GitHub
* Pytest
* FastAPI Swagger / OpenAPI

---

## 📂 Project Structure

```text
planetpulse/
│
├── backend/
│   ├── app/
│   │   ├── carbon/
│   │   │   └── calculator.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── goal.py
│   │   │   └── activity.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── activity.py
│   │   │   ├── goal.py
│   │   │   ├── trend.py
│   │   │   └── ...
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── activity_service.py
│   │   │   ├── goal_service.py
│   │   │   ├── trend_service.py
│   │   │   ├── what_if_service.py
│   │   │   └── insights_service.py
│   │   │
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── activities.py
│   │   │   ├── dashboard.py
│   │   │   ├── trend.py
│   │   │   ├── goal.py
│   │   │   ├── what_if.py
│   │   │   └── insights.py
│   │   │
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── API.md
│   └── DECISIONS.md
│
└── frontend/
```

---

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd planetpulse
```

### 2. Switch to the Development Branch

```bash
git checkout Ayush_planet_pulse
```

### 3. Setup Backend

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run the Backend

```bash
uvicorn app.main:app --reload --port 8001
```

Backend:

```text
http://localhost:8001
```

Health check:

```text
http://localhost:8001/api/health
```

API documentation:

```text
http://localhost:8001/docs
```

---

## 🧪 Testing

The backend includes automated tests covering authentication, activities, dashboard calculations, trends, goals, what-if analysis, insights, carbon calculations, and API compatibility.

Current backend validation:

```text
120 passed
```

Run the test suite with:

```bash
python -m pytest -q
```

---

## 🔌 API Overview

### Authentication

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

### Activities

```text
GET    /api/activities
POST   /api/activities
DELETE /api/activities/{activity_id}
```

### Dashboard

```text
GET /api/dashboard
```

### Trends

```text
GET /api/trend
```

### Goals

```text
GET /api/goal
PUT /api/goal
```

### What-If Analysis

```text
POST /api/what-if
```

### Insights

```text
GET /api/insights
```

### Health

```text
GET /api/health
```

Detailed API information is available in:

```text
backend/API.md
```

---

## 🧮 Carbon Calculation

PlanetPulse uses a centralized carbon calculation engine.

```text
User Activity
      ↓
Activity Normalization
      ↓
Carbon Calculation Engine
      ↓
CO₂e Emission
      ↓
Database
      ↓
Dashboard / Trends / Insights / What-If
```

Keeping the calculation logic centralized helps maintain consistent emission calculations across different features.

---

## 🔒 Security

The backend includes:

* Password hashing using a salted `scrypt` configuration
* JWT authentication
* Protected user-specific routes
* User-scoped activity and goal data
* Configurable token expiration
* CORS configuration

Sensitive credentials and secrets should be provided through environment variables and should not be committed to GitHub.

---

## 📌 Current Development Status

### Backend

* ✅ FastAPI backend
* ✅ Database models
* ✅ Authentication
* ✅ Activity tracking
* ✅ Carbon calculation engine
* ✅ Dashboard API
* ✅ Trend API
* ✅ Monthly goals
* ✅ What-If analysis
* ✅ Rule-based insights
* ✅ CORS configuration
* ✅ API documentation
* ✅ Automated testing
* ✅ GitHub integration

### Frontend

* 🚧 Frontend integration and end-to-end testing

---

## 🎯 Project Objective

PlanetPulse aims to make personal carbon tracking easier to understand by connecting everyday activities with measurable environmental impact.

Instead of only showing an emission number, the platform combines:

**Track → Analyze → Compare → Set Goals → Explore Alternatives**

to help users understand how their daily choices affect their estimated carbon footprint.

---

## 👨‍💻 Developer

**Ayush Gupta**

**Focus:** Data Analytics, Python, SQL, Power BI & Software Development

---

## 📄 License

This project is developed for educational and portfolio purposes.
