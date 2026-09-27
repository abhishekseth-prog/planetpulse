# 🌍 Planet Pulse

## Personal Carbon Intelligence Platform

> **Understand your footprint. Build better habits. Make every day a little lighter.**

Planet Pulse is a personal carbon intelligence platform that helps users **track, understand, analyze, and reduce their carbon footprint** using real activity data.

---

## 🚀 Live Demo

### 🌐 Frontend

**https://planetpulse-2cq5.vercel.app/**

### ⚡ Backend API

**https://planetpulse-0adp.onrender.com/**

### 🔗 API Health Check

**https://planetpulse-0adp.onrender.com/api/health**

---

## ✨ Key Features

### 🔐 Authentication

* User registration and login
* JWT-based authentication
* Secure password hashing
* Protected API endpoints
* User-specific data isolation

### 📊 Personal Dashboard

* Total carbon emissions
* Category-wise emissions
* Recent activities
* Carbon trends
* Monthly goals
* Carbon Score
* Personalized daily action
* Monthly comparison
* Category insights

### 🌱 Activity Tracking

Track real-world activities such as:

* 🚗 Travel
* ⚡ Electricity
* 🍽️ Food

Carbon emissions are calculated using the centralized carbon calculation engine.

### 🤖 Carbon Coach

The Carbon Coach provides personalized insights based on the user's actual recorded activities and carbon emissions.

### 🔮 Impact Simulator

The What-If / Impact Simulator allows users to compare their current activity with alternative choices.

Example:

```text
Current Activity
Car · 35 km
4.2 kg CO₂

        ↓

Alternative
Metro · 35 km
1.4 kg CO₂

Potential Reduction
2.8 kg CO₂
```

The simulator uses real user activity data and the existing backend carbon calculation engine.

### 📈 Analytics & Trends

* Carbon trend analysis
* Category-wise emissions
* Monthly comparisons
* Historical activity analysis

### 🎯 Monthly Goals

* Set monthly carbon goals
* Track progress
* Update goals
* View current achievement

### 📱 Responsive Design

Planet Pulse is designed for:

* Desktop
* Tablet
* Mobile

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       USER          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │       Vercel        │
                    └──────────┬──────────┘
                               │
                         REST API / HTTPS
                               │
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    │       Render        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      MySQL          │
                    │   Cloud Database    │
                    └─────────────────────┘
```

---

# 🛠️ Technology Stack

## Frontend

* React
* Vite
* JavaScript
* CSS

## Backend

* Python
* FastAPI
* Uvicorn
* JWT Authentication
* Python-dotenv

## Database

* MySQL
* MySQL Connector/Python

## Deployment

* **Frontend:** Vercel
* **Backend:** Render
* **Database:** Cloud MySQL

---

# 📂 Project Structure

```text
planetpulse/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── tests/
│
├── README.md
└── .gitignore
```

---

# ⚙️ Local Installation

## 1. Clone Repository

```bash
git clone https://github.com/abhishekseth-prog/planetpulse.git
cd planetpulse
```

Switch to the project branch if required:

```bash
git checkout PLANET-PULSE
```

---

# 🔧 Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=planetpulse

JWT_SECRET_KEY=your_secret_key

CORS_ORIGINS=http://localhost:5173
```

Start the backend:

```bash
uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

---

# 💻 Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Configure the frontend API URL using the environment variable required by the project.

Example:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# ☁️ Production Deployment

## Frontend — Vercel

Live frontend:

**https://planetpulse-2cq5.vercel.app/**

The production frontend communicates with the FastAPI backend through HTTPS.

---

## Backend — Render

Live backend:

**https://planetpulse-0adp.onrender.com/**

Render configuration:

```text
Root Directory:
backend

Build Command:
pip install -r requirements.txt

Start Command:
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

# 🔐 Environment Variables

### Backend

```env
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=
JWT_SECRET_KEY=
CORS_ORIGINS=
```

### Frontend

The frontend production API URL should point to:

```text
https://planetpulse-0adp.onrender.com
```

> ⚠️ Never commit `.env` files, passwords, database credentials, JWT secrets, or API keys to GitHub.

---

# 🧮 Carbon Calculation Engine

Planet Pulse uses a centralized carbon calculation engine for consistent calculations across the application.

The calculation engine is used by:

* Activity Tracking
* Dashboard
* Analytics
* Carbon Trends
* What-If Simulator
* Category Insights
* Personalized Actions

This keeps carbon calculations consistent throughout the platform.

---

# 🧪 Testing & Quality Assurance

The application has been tested for:

* Authentication
* Registration
* Login
* JWT authentication
* User data isolation
* Activity creation
* Dashboard calculations
* Carbon trends
* Monthly goals
* Carbon Coach
* Category insights
* Monthly comparison
* What-If calculations
* Impact Simulator
* Empty states
* API error handling
* Responsive layouts
* Frontend production build
* Frontend linting

---

# 🔄 Core User Flow

```text
Create Account
      ↓
Login
      ↓
Personal Dashboard
      ↓
Record Activity
      ↓
Carbon Calculation
      ↓
Analytics & Trends
      ↓
Carbon Coach
      ↓
Monthly Goals
      ↓
Impact Simulator
      ↓
Make Better Choices
```

---

# 🎯 Project Objectives

Planet Pulse aims to help users:

1. Understand their personal carbon footprint
2. Track everyday activities
3. Identify high-impact categories
4. Set monthly reduction goals
5. Compare alternative choices
6. Receive personalized insights
7. Build more sustainable habits

---

# 🔮 Future Enhancements

Potential future improvements:

* Advanced AI-powered recommendations
* Achievement system
* Goal streaks
* Notifications
* Data export
* More detailed analytics
* Sustainability education
* Additional activity categories
* Advanced personalization

---

# 👨‍💻 Project Information

**Project:** Planet Pulse
**Type:** Personal Carbon Intelligence Platform

### Live Application

🌐 **Frontend:**
https://planetpulse-2cq5.vercel.app/

⚡ **Backend:**
https://planetpulse-0adp.onrender.com/

### Built With

```text
React + FastAPI + MySQL
```

### Deployed With

```text
Vercel + Render + Cloud MySQL
```

---

## 📄 License

This project can be released under the license selected by the project owner.
