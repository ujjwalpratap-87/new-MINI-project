from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WeatherRequest(BaseModel):
    city: str = Field(..., min_length=2, max_length=80)


class PredictionRequest(WeatherRequest):
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    pressure: float | None = None
    weather_condition: str | None = None


class PredictionResponse(BaseModel):
    city: str
    timestamp: datetime
    temperature: float
    humidity: float
    wind_speed: float
    pressure: float
    weather_condition: str
    predicted_aqi: float
    aqi_label: str
    recommendation: str
    model_name: str
    source: str | None = None


class TrainResponse(BaseModel):
    best_model: str
    metrics: dict[str, float]
    leaderboard: list[dict[str, Any]]
