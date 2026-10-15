import hashlib
import json
from fastapi import APIRouter, HTTPException, Query
from app.db.mongodb import get_cached_analysis, save_analysis
from app.schemas.hazard import AnalyzeRequest
from app.services.hazard_service import analyze

router = APIRouter(prefix="/hazards", tags=["hazards"])


def _key(payload: AnalyzeRequest) -> str:
    serialized = json.dumps(payload.model_dump(), sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


async def _get_or_analyze(payload: AnalyzeRequest) -> dict:
    key = _key(payload)
    cached = await get_cached_analysis(key)
    if cached:
        return cached
    result = await analyze(payload)
    await save_analysis(key, result)
    return result


@router.post("/analyze")
async def analyze_hazards(payload: AnalyzeRequest):
    return await _get_or_analyze(payload)


@router.get("/summary")
async def get_summary(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    start_year: int = Query(ge=1940, le=2100),
    end_year: int = Query(ge=1940, le=2100),
    hazard: str = Query(default="heatwave", pattern="^(heatwave|heavy_rainfall|drought)$"),
):
    try:
        payload = AnalyzeRequest(
            latitude=latitude,
            longitude=longitude,
            start_year=start_year,
            end_year=end_year,
            hazard=hazard,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return await _get_or_analyze(payload)


@router.get("/timeseries")
async def get_timeseries(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    start_year: int = Query(ge=1940, le=2100),
    end_year: int = Query(ge=1940, le=2100),
    hazard: str = Query(default="heatwave", pattern="^(heatwave|heavy_rainfall|drought)$"),
):
    payload = AnalyzeRequest(
        latitude=latitude, longitude=longitude,
        start_year=start_year, end_year=end_year, hazard=hazard,
    )
    result = await _get_or_analyze(payload)
    return {"hazard": result["hazard"], "period": result["period"], "timeseries": result["timeseries"]}


@router.get("/events")
async def get_events(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    start_year: int = Query(ge=1940, le=2100),
    end_year: int = Query(ge=1940, le=2100),
    hazard: str = Query(default="heatwave", pattern="^(heatwave|heavy_rainfall|drought)$"),
):
    payload = AnalyzeRequest(
        latitude=latitude, longitude=longitude,
        start_year=start_year, end_year=end_year, hazard=hazard,
    )
    result = await _get_or_analyze(payload)
    return {"hazard": result["hazard"], "events": result["events"]}
