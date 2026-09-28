# PlanetPulse — Personal Carbon Intelligence Platform

**PlanetPulse** is a full-stack environmental impact tracking platform that helps users understand and monitor the carbon footprint associated with their everyday activities, including **travel, food, and electricity consumption**.

The platform combines activity tracking, carbon-emission calculations, analytics, goal management, and what-if analysis into a single dashboard to help users better understand their environmental impact.

## 🌐 Live Application

* **Frontend:** https://planetpulse-2cq5.vercel.app/
* **Backend API:** https://planetpulse-0adp.onrender.com/
* **API Documentation:** https://planetpulse-0adp.onrender.com/docs

---

## 🚀 Key Features

### 🔐 Authentication & User Management

* User registration and login
* JWT-based authentication
* Protected API routes
* User-specific activity and analytics data

### 📊 Carbon Impact Dashboard

* Overview of personal carbon emissions
* Activity-based impact breakdown
* Key environmental performance indicators
* Historical impact visualization

### 🌱 Activity Tracking

Users can record daily activities across major emission categories:

* 🚗 **Travel**
* 🍽️ **Food**
* ⚡ **Electricity**

Each activity is processed through the carbon calculation engine to estimate its associated emissions.

### 📈 Analytics & Trends

* Daily and monthly emission trends
* Category-wise impact analysis
* Historical activity insights
* Data-driven visualizations for understanding emission patterns

### 🎯 Monthly Goals

* Set personal carbon-reduction goals
* Track progress toward monthly targets
* Monitor current performance against goals

### 🔄 Impact Simulator

The **What-If / Impact Simulator** allows users to explore hypothetical changes in their activities and understand how those changes could affect their estimated carbon footprint.

### 💡 Carbon Coach

Provides practical insights based on tracked activities to help users identify areas where their environmental impact can potentially be reduced.

### 📱 Responsive Interface

* Modern React-based interface
* Responsive dashboard
* Component-based frontend architecture
* REST API integration with the backend

---

## 🏗️ System Architecture

```text
┌──────────────────────────────┐
│        React + Vite          │
│          Frontend            │
│           Vercel             │
└──────────────┬───────────────┘
               │
               │ REST API
               ▼
┌──────────────────────────────┐
│        FastAPI Backend       │
│           Render             │
│                              │
│ Authentication               │
│ Activity Management          │
│ Carbon Calculations          │
│ Analytics & Trends           │
│ Goals & What-If Analysis     │
└──────────────┬───────────────┘
               │
               │ SQLAlchemy
               ▼
┌──────────────────────────────┐
│      PostgreSQL Database     │
│           Render             │
└──────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend

* React.js
* Vite
* JavaScript
* HTML5
* CSS3
* REST API integration
* Vercel

### Backend

* Python
* FastAPI
* SQLAlchemy
* Uvicorn
* JWT Authentication
* RESTful APIs
* Render

### Database

* PostgreSQL
* SQLAlchemy ORM

### Deployment

* **Frontend:** Vercel
* **Backend:** Render
* **Database:** Render PostgreSQL

---

## 🔄 Core User Flow

```text
User Registration / Login
          ↓
     User Dashboard
          ↓
   Record Daily Activity
          ↓
 Carbon Calculation Engine
          ↓
   Store Activity Data
          ↓
 Analytics & Trend Processing
          ↓
 Dashboard Insights
          ↓
 Goals / Carbon Coach / What-If Analysis
```

---

## 🧮 Carbon Calculation Engine

PlanetPulse processes user activity data and converts it into estimated carbon emissions using activity-specific calculation logic.

The calculation pipeline follows the general flow:

```text
Activity Input
      ↓
Activity Validation
      ↓
Category-Specific Calculation
      ↓
Emission Estimate
      ↓
Database Storage
      ↓
Analytics & Visualization
```

The calculation layer is designed to keep emission logic separate from the API and presentation layers, making the backend easier to maintain and extend.

---

## 📁 Project Structure

```text
planetpulse/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   └── ...
│   ├── requirements.txt
│   └── ...
│
└── README.md
```

---

## ⚙️ Local Development

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd planetpulse
```

### 2. Backend Setup

```bash
cd backend

python -m venv venv
```

Activate the virtual environment:

**Windows**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME
JWT_SECRET_KEY=your_secret_key
CORS_ORIGINS=http://localhost:5173
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 🔒 Environment Variables

### Backend

```env
DATABASE_URL=
JWT_SECRET_KEY=
CORS_ORIGINS=
```

### Frontend

```env
VITE_API_URL=
```

**Never commit `.env` files, database credentials, JWT secrets, or other sensitive configuration to the repository.**

---

## ☁️ Deployment

PlanetPulse uses a separated frontend/backend architecture:

| Component         | Technology      | Deployment |
| ----------------- | --------------- | ---------- |
| Frontend          | React + Vite    | Vercel     |
| Backend           | FastAPI         | Render     |
| Database          | PostgreSQL      | Render     |
| API Documentation | FastAPI Swagger | Render     |

The frontend communicates with the deployed FastAPI backend through REST APIs, while the backend manages authentication, business logic, carbon calculations, and database operations.

---

## 🎯 Project Objectives

PlanetPulse was developed to:

* Track carbon emissions from everyday activities
* Provide a centralized view of personal environmental impact
* Transform activity data into meaningful analytics
* Help users monitor reduction goals
* Provide what-if analysis for potential lifestyle changes
* Demonstrate full-stack application development with a data-driven backend

---

## 🔮 Future Enhancements

Potential future improvements include:

* More detailed emission-factor datasets
* Advanced personalization of recommendations
* Additional activity categories
* Improved comparative analytics
* Exportable environmental impact reports
* Extended visualization and reporting capabilities

---

## 👨‍💻 Author

**Ayush Gupta**

