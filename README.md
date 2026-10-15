# Climate Hazard Analyzer

A full-stack starter application for exploring historical climate hazards.

## Stack
- Frontend: React + Vite + Recharts + Leaflet
- Backend: FastAPI + Pandas + HTTPX + Motor
- Database: MongoDB
- Data source: Open-Meteo Historical Weather API

## Features
- Region selection using latitude/longitude (city presets included)
- Hazard selector (Heatwave selected by default)
- Date-range selection
- Historical weather ingestion and caching
- Heatwave detection using a fixed 95th-percentile reference threshold and a minimum consecutive-day rule
- Annual event frequency, average duration, linear trend, and a simple comparison insight
- Time-series chart and location map
- MongoDB persistence with an in-memory fallback for local demos


## Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB (local or hosted). If MongoDB is unavailable, the backend uses an in-memory cache for demo purposes.

## Run the backend (Windows PowerShell)
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

## Run the frontend (new terminal)
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open the URL printed by Vite, normally http://localhost:5173.

## MongoDB
The default URI is `mongodb://localhost:27017` and database is `climate_hazard_analyzer`.
Set `MONGODB_URI` in `backend/.env` for MongoDB Atlas or another server.

## API examples
```http
GET http://127.0.0.1:8000/api/regions
GET http://127.0.0.1:8000/api/hazards/summary?latitude=10.0&longitude=76.3&start_year=1990&end_year=2020&hazard=heatwave
GET http://127.0.0.1:8000/api/hazards/timeseries?latitude=10.0&longitude=76.3&start_year=1990&end_year=2020&hazard=heatwave
POST http://127.0.0.1:8000/api/hazards/analyze
Content-Type: application/json

{
  "latitude": 10.0,
  "longitude": 76.3,
  "start_year": 1990,
  "end_year": 2020,
  "hazard": "heatwave",
  "min_consecutive_days": 3
}
```

## Notes about the method
- The API downloads daily maximum temperature and precipitation from Open-Meteo.
- The reference threshold is calculated from all available daily maximum temperatures in 1991–2020 for the selected point. For dates outside that reference period, the same threshold is applied.
- This starter detects events at one coordinate. A custom bounding box needs a defined grid and an aggregation method before results can be interpreted as region-wide.
- Historical coverage depends on the Open-Meteo dataset and requested dates.
- Initial ingestion can take a while for multi-decade ranges. The app caches raw daily records and derived results.
- Never present placeholder/demo data as measured observations. If a request fails, the UI displays an error.
