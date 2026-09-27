# Planet Pulse

PlanetPulse — Personal Carbon Footprint & Impact Decision Platform.

Planet Pulse is a sustainability dashboard for tracking personal carbon-footprint estimates. It records travel, electricity, and food activities, then shows account-specific totals, trends, goals, What-If comparisons, and sustainability insights.

## Features

- Email/password authentication with signed JWT access tokens
- User-specific activity, dashboard, analytics, trend, and goal data
- Travel, electricity, and food activity tracking
- Centralized carbon calculations with configurable emission factors
- Monthly goal progress and What-If comparisons
- Rule-based sustainability insights based on the authenticated user's data
- Responsive React dashboard with API loading and error states

## Tech stack

- **Frontend:** React 19, Vite, CSS
- **Backend:** Python, FastAPI, Pydantic, JWT authentication
- **Database:** MySQL with `mysql-connector-python`

## Project layout

```text
backend/       FastAPI app, API routes, calculations, schema, migrations, tests
frontend/      React/Vite dashboard
DECISIONS.md   Carbon-factor sources and prototype assumptions
```

## Requirements

- Node.js and npm
- Python 3.10 or newer
- MySQL 8 or a compatible MySQL server

## Configure MySQL and the backend

1. Create a MySQL database, or choose a database name for your local configuration.
2. In PowerShell:

   ```powershell
   cd backend
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

3. Edit `backend/.env` with your local database host, username, password, database name, and a random `JWT_SECRET_KEY` of at least 32 bytes. Keep this file private; it is ignored by Git.
4. For a fresh database, apply `backend/schema.sql`. For an existing Planet Pulse database, run `python migrate_auth.py` from the `backend` directory. The migration is additive and preserves existing activity data.
5. Start the API from `backend`:

   ```powershell
   uvicorn main:app --reload --port 8001
   ```

   The API health check is at `http://127.0.0.1:8001/api/health`; interactive docs are at `http://127.0.0.1:8001/docs`.

## Run the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite serves the app at `http://127.0.0.1:5173`. The frontend uses `http://127.0.0.1:8001` by default. To point it elsewhere, set `VITE_API_URL` in a local `frontend/.env` file. Configure the matching comma-separated frontend origins in backend `CORS_ORIGINS` when running outside local development.

## Checks

From `frontend`:

```powershell
npm run lint
npm run build
```

The backend end-to-end verification script is `backend/tests/verify_auth_flow.py`. It requires the backend API and configured MySQL database to be running. It creates disposable accounts and removes only those accounts and their test rows during cleanup.

For API request/response details and local run notes, see [backend/API.md](backend/API.md). Carbon-factor sources and limitations are documented in [DECISIONS.md](DECISIONS.md).

## Environment files and secrets

Use `backend/.env.example` as the placeholder template. Never commit `.env` files, real database credentials, JWT secrets, API keys, or other private configuration. The root `.gitignore` excludes local environment files, virtual environments, dependencies, build output, and local database files.
