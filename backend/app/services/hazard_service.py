from datetime import date
import numpy as np
import pandas as pd
from app.core.config import settings
from app.schemas.hazard import AnalyzeRequest
from app.services.weather_service import fetch_daily_weather


def _runs(mask: list[bool], min_days: int) -> list[tuple[int, int]]:
    events = []
    start = None
    for i, hot in enumerate(mask):
        if hot and start is None:
            start = i
        if start is not None and (not hot or i == len(mask) - 1):
            end = i - 1 if not hot else i
            if end - start + 1 >= min_days:
                events.append((start, end))
            start = None
    return events


def _linear_trend(points: list[dict]) -> dict:
    valid = [p for p in points if p.get("frequency") is not None]
    if len(valid) < 2:
        return {"slope_events_per_year": None, "direction": "insufficient_data"}
    x = np.array([p["year"] for p in valid], dtype=float)
    y = np.array([p["frequency"] for p in valid], dtype=float)
    slope = float(np.polyfit(x, y, 1)[0])
    direction = "increasing" if slope > 0.01 else "decreasing" if slope < -0.01 else "approximately_stable"
    return {"slope_events_per_year": round(slope, 4), "direction": direction}


async def analyze(request: AnalyzeRequest) -> dict:
    # Include reference period before the selected analysis range to calculate a consistent threshold.
    fetch_start_year = min(request.start_year, settings.reference_start_year)
    fetch_end_year = max(request.end_year, settings.reference_end_year)
    fetch_start = date(fetch_start_year, 1, 1)
    fetch_end = date(fetch_end_year, 12, 31)
    rows = await fetch_daily_weather(
        request.latitude, request.longitude, fetch_start, fetch_end
    )
    df = pd.DataFrame(rows)
    if df.empty:
        return _empty_result(request)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["temperature_max"] = pd.to_numeric(df["temperature_max"], errors="coerce")
    df["precipitation_sum"] = pd.to_numeric(df["precipitation_sum"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    df["year"] = df["date"].dt.year

    if request.hazard == "heatwave":
        reference = df[
            (df["year"] >= settings.reference_start_year)
            & (df["year"] <= settings.reference_end_year)
        ]["temperature_max"].dropna()
        if reference.empty:
            reference = df["temperature_max"].dropna()
        threshold = float(reference.quantile(0.95)) if not reference.empty else None
        df["qualifies"] = df["temperature_max"] > threshold if threshold is not None else False
        df["event_day"] = False
        events = []
        valid = df["temperature_max"].notna().to_numpy()
        # Break sequences across missing observations and gaps in the daily calendar.
        qualifies = df["qualifies"].fillna(False).to_numpy(dtype=bool)
        dates = df["date"].tolist()
        segments = []
        segment_start = 0
        for i in range(1, len(df) + 1):
            if i == len(df) or (dates[i] - dates[i-1]).days != 1 or not valid[i] if i < len(df) else True:
                if segment_start < i:
                    segments.append((segment_start, i))
                segment_start = i
        for seg_start, seg_end in segments:
            local_mask = qualifies[seg_start:seg_end].tolist()
            for a, b in _runs(local_mask, request.min_consecutive_days):
                start_idx, end_idx = seg_start + a, seg_start + b
                df.loc[start_idx:end_idx, "event_day"] = True
                segment = df.loc[start_idx:end_idx]
                events.append({
                    "start_date": segment["date"].iloc[0].date().isoformat(),
                    "end_date": segment["date"].iloc[-1].date().isoformat(),
                    "duration_days": int(len(segment)),
                    "peak_temperature_c": round(float(segment["temperature_max"].max()), 2),
                    "excess_temperature_c_days": round(float((segment["temperature_max"] - threshold).sum()), 2),
                })
        metric_column = "event_day"
        # Count events by their start year.
        event_year_counts = {}
        for event in events:
            y = int(event["start_date"][:4])
            event_year_counts[y] = event_year_counts.get(y, 0) + 1
        threshold_value = round(threshold, 2) if threshold is not None else None
        definition = f"At least {request.min_consecutive_days} consecutive days above the {settings.reference_start_year}-{settings.reference_end_year} 95th percentile."
    elif request.hazard == "heavy_rainfall":
        reference = df[
            (df["year"] >= settings.reference_start_year)
            & (df["year"] <= settings.reference_end_year)
        ]["precipitation_sum"].dropna()
        if reference.empty:
            reference = df["precipitation_sum"].dropna()
        threshold = float(reference.quantile(0.95)) if not reference.empty else None
        df["qualifies"] = (df["precipitation_sum"] > threshold) if threshold is not None else False
        events = []
        for idx, row in df[df["qualifies"]].iterrows():
            events.append({
                "start_date": row["date"].date().isoformat(),
                "end_date": row["date"].date().isoformat(),
                "duration_days": 1,
                "peak_rainfall_mm": round(float(row["precipitation_sum"]), 2),
            })
        event_year_counts = {}
        for event in events:
            y = int(event["start_date"][:4])
            event_year_counts[y] = event_year_counts.get(y, 0) + 1
        threshold_value = round(threshold, 2) if threshold is not None else None
        definition = f"Daily precipitation above the {settings.reference_start_year}-{settings.reference_end_year} 95th percentile."
    else:
        # Simple exploratory drought proxy: rolling 90-day precipitation below its reference-period 10th percentile.
        df["rolling_precip"] = df["precipitation_sum"].rolling(90, min_periods=75).sum()
        reference = df[
            (df["year"] >= settings.reference_start_year)
            & (df["year"] <= settings.reference_end_year)
        ]["rolling_precip"].dropna()
        if reference.empty:
            reference = df["rolling_precip"].dropna()
        threshold = float(reference.quantile(0.10)) if not reference.empty else None
        df["qualifies"] = (df["rolling_precip"] < threshold) if threshold is not None else False
        events = []
        # Represent each qualifying day as a proxy observation, not an independent drought event.
        event_year_counts = {}
        for _, row in df[df["qualifies"]].iterrows():
            y = int(row["year"])
            event_year_counts[y] = event_year_counts.get(y, 0) + 1
        threshold_value = round(threshold, 2) if threshold is not None else None
        definition = "Exploratory proxy: 90-day precipitation total below its reference-period 10th percentile; counts are qualifying days, not distinct drought events."

    selected = df[(df["year"] >= request.start_year) & (df["year"] <= request.end_year)].copy()
    timeseries = []
    for year in range(request.start_year, request.end_year + 1):
        year_df = selected[selected["year"] == year]
        if request.hazard == "heatwave":
            count = event_year_counts.get(year, 0)
            avg_duration = [
                e["duration_days"] for e in events if int(e["start_date"][:4]) == year
            ]
            timeseries.append({
                "year": year,
                "frequency": count,
                "average_duration_days": round(float(np.mean(avg_duration)), 2) if avg_duration else 0,
                "mean_max_temperature_c": round(float(year_df["temperature_max"].mean()), 2) if year_df["temperature_max"].notna().any() else None,
            })
        elif request.hazard == "heavy_rainfall":
            timeseries.append({
                "year": year,
                "frequency": event_year_counts.get(year, 0),
                "annual_precipitation_mm": round(float(year_df["precipitation_sum"].sum()), 2) if year_df["precipitation_sum"].notna().any() else None,
            })
        else:
            timeseries.append({
                "year": year,
                "frequency": event_year_counts.get(year, 0),
                "qualifying_days": event_year_counts.get(year, 0),
            })

    selected_events = [
        e for e in events
        if request.start_year <= int(e["start_date"][:4]) <= request.end_year
    ]
    trend = _linear_trend(timeseries)
    midpoint = request.start_year + (request.end_year - request.start_year) // 2
    first = [p["frequency"] for p in timeseries if request.start_year <= p["year"] < midpoint]
    second = [p["frequency"] for p in timeseries if midpoint <= p["year"] <= request.end_year]
    baseline = float(np.mean(first)) if first else 0.0
    recent = float(np.mean(second)) if second else 0.0
    if baseline > 0:
        change = round((recent - baseline) / baseline * 100, 1)
        insight = f"{request.hazard.replace('_', ' ').title()} frequency changed by {change}% between the earlier and later halves of the selected period."
    elif recent > 0:
        change = None
        insight = "No events were observed in the earlier comparison period, so percentage change is undefined; the later period has detected events."
    else:
        change = 0.0
        insight = "No qualifying events were detected in either comparison period."
    avg_duration = round(float(np.mean([e["duration_days"] for e in selected_events])), 2) if selected_events else None
    return {
        "region": {"latitude": request.latitude, "longitude": request.longitude},
        "hazard": request.hazard,
        "period": {"start_year": request.start_year, "end_year": request.end_year},
        "threshold": threshold_value,
        "metrics": {
            "total_events": len(selected_events) if request.hazard != "drought" else sum(p["frequency"] for p in timeseries),
            "average_duration_days": avg_duration,
            "annual_frequency_change_percent": change,
            "trend": trend,
        },
        "timeseries": timeseries,
        "events": selected_events[-500:],
        "insight": insight,
        "methodology": {
            "definition": definition,
            "reference_period": {
                "start_year": settings.reference_start_year,
                "end_year": settings.reference_end_year,
            },
            "caveat": "Point-based exploratory analysis. Results depend on dataset, missing values, threshold definition, and selected reference period.",
        },
    }


def _empty_result(request: AnalyzeRequest) -> dict:
    return {
        "region": {"latitude": request.latitude, "longitude": request.longitude},
        "hazard": request.hazard,
        "period": {"start_year": request.start_year, "end_year": request.end_year},
        "threshold": None,
        "metrics": {"total_events": 0, "average_duration_days": None, "annual_frequency_change_percent": None, "trend": {"direction": "insufficient_data", "slope_events_per_year": None}},
        "timeseries": [],
        "events": [],
        "insight": "No observations were available for this request.",
        "methodology": {"definition": "No data available."},
    }
