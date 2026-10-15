import hashlib
from datetime import date
import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.db.mongodb import get_cached_weather, save_weather


def weather_cache_key(latitude: float, longitude: float, start: date, end: date) -> str:
    # Rounded coordinates keep cache keys stable while retaining useful point precision.
    return f"{latitude:.4f}:{longitude:.4f}:{start.isoformat()}:{end.isoformat()}"


async def fetch_daily_weather(latitude: float, longitude: float, start: date, end: date) -> list[dict]:
    cache_key = weather_cache_key(latitude, longitude, start, end)
    cached = await get_cached_weather(cache_key)
    if cached:
        return cached

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "temperature_2m_max,precipitation_sum",
        "timezone": "UTC",
        "temperature_unit": "celsius",
    }
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.get(settings.open_meteo_base_url, params=params)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"Weather provider request failed: {exc}") from exc

    daily = payload.get("daily") or {}
    dates = daily.get("time") or []
    temps = daily.get("temperature_2m_max") or []
    rainfall = daily.get("precipitation_sum") or []
    if not dates:
        raise HTTPException(status_code=502, detail="Weather provider returned no daily observations.")

    rows = []
    for index, day in enumerate(dates):
        temp = temps[index] if index < len(temps) else None
        rain = rainfall[index] if index < len(rainfall) else None
        rows.append({
            "date": day,
            "temperature_max": temp,
            "precipitation_sum": rain,
        })
    await save_weather(cache_key, rows)
    return rows
