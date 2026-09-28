# 🌍 PlanetPulse

PlanetPulse is a web-based environmental impact tracking platform designed to help users monitor their daily activities and understand their environmental footprint.

The application provides a user-friendly dashboard where users can record activities, calculate environmental impact, and view their data through analytics.

## 🔗 Live Demo

### 🎨 Frontend

**PlanetPulse Web App:**
https://planetpulse-2cq5.vercel.app/

### ⚙️ Backend API

**PlanetPulse Backend:**
https://planetpulse-0adp.onrender.com

### 📚 API Documentation

**Swagger UI:**
https://planetpulse-0adp.onrender.com/docs

---

## ✨ Features

* 🔐 User Registration & Login
* 🌱 Environmental Impact Tracking
* 📊 Interactive Dashboard
* 📈 Activity & Impact Analytics
* 📝 Add and manage environmental activities
* 🗂️ Category-based activity tracking
* 🔄 Frontend–Backend API integration
* 🗄️ MySQL database integration
* 🔒 Authentication and authorization

---

## 🛠️ Tech Stack

### Frontend

* React.js
* JavaScript
* HTML5
* CSS3
* REST APIs
* Vercel

### Backend

* Python
* FastAPI
* SQLAlchemy
* JWT Authentication
* REST API
* Render

### Database

* MySQL

---

## 🏗️ Project Architecture

```text
                    ┌─────────────────────┐
                    │     PlanetPulse     │
                    │      Frontend       │
                    │      React.js       │
                    └──────────┬──────────┘
                               │
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │     PlanetPulse     │
                    │       Backend       │
                    │      FastAPI        │
                    └──────────┬──────────┘
                               │
                               │ SQLAlchemy
                               ▼
                    ┌─────────────────────┐
                    │       MySQL         │
                    │      Database       │
                    └─────────────────────┘
```

---

## 🚀 Live Application

Visit the application:

👉 **https://planetpulse-2cq5.vercel.app/**

The frontend communicates with the deployed FastAPI backend through REST APIs.

---

## ⚙️ Backend API

The deployed backend is available at:

👉 **https://planetpulse-0adp.onrender.com**

### API Documentation

FastAPI automatically provides interactive Swagger documentation:

👉 **https://planetpulse-0adp.onrender.com/docs**

You can use Swagger UI to:

* View available API endpoints
* Test API requests
* Register users
* Login users
* Authorize using JWT
* Test protected endpoints
* Check API responses

---

## 💻 Run Locally

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd PlanetPulse
```

### 2. Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally run at:

```text
http://localhost:5173
```

---

### 3. Backend Setup

Navigate to the backend directory:

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

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Backend will normally run at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🔐 Environment Variables

Create a `.env` file in the backend and configure your database and authentication settings.

Example:

```env
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@HOST/DATABASE_NAME

SECRET_KEY=your_secret_key

ALGORITHM=HS256
```

For production deployment, configure these variables in your hosting platform rather than committing `.env` to GitHub.

---

## 📂 Project Structure

```text
PlanetPulse/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── database/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
└── README.md
```

> Adjust the folder structure above if your actual repository uses different folder names.

---

## 🔄 Application Flow

```text
User
  │
  ▼
React Frontend
  │
  │ HTTP Request
  ▼
FastAPI Backend
  │
  │ Authentication / Business Logic
  ▼
MySQL Database
  │
  ▼
FastAPI Response
  │
  ▼
React Dashboard
```

---

## 📌 Deployment

| Component | Platform        | URL                                        |
| --------- | --------------- | ------------------------------------------ |
| Frontend  | Vercel          | https://planetpulse-2cq5.vercel.app/       |
| Backend   | Render          | https://planetpulse-0adp.onrender.com      |
| API Docs  | FastAPI Swagger | https://planetpulse-0adp.onrender.com/docs |
| Database  | MySQL           | Production Database                        |

---

## 🎯 Project Goal

The goal of PlanetPulse is to make environmental impact tracking simple and accessible by allowing users to record activities and understand their contribution to environmental sustainability through data and analytics.

---

## 👨‍💻 Author

**Akhilesh Kumar Yadav**

B.Tech Computer Science & Engineering

### Skills

* Python
* SQL / MySQL
* React.js
* FastAPI
* JavaScript
* Excel
* Power BI
* Data Analytics

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.
