from typing import Literal
from pydantic import BaseModel, Field, model_validator


HazardType = Literal["heatwave", "heavy_rainfall", "drought"]


class AnalyzeRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    start_year: int = Field(ge=1940, le=2100)
    end_year: int = Field(ge=1940, le=2100)
    hazard: HazardType = "heatwave"
    min_consecutive_days: int = Field(default=3, ge=2, le=30)

    @model_validator(mode="after")
    def validate_years(self):
        if self.end_year < self.start_year:
            raise ValueError("end_year must be greater than or equal to start_year")
        return self


class AnalyzeResponse(BaseModel):
    region: dict
    hazard: str
    period: dict
    threshold: float | None = None
    metrics: dict
    timeseries: list[dict]
    events: list[dict]
    insight: str
    methodology: dict
