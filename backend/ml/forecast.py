from __future__ import annotations

from typing import Any

import pandas as pd

from backend.services.weather import fetch_weather_forecast


def build_forecast_frame(city: str, horizon_hours: int = 24, api_key: str | None = None) -> pd.DataFrame:
    weather_frame = fetch_weather_forecast(city, api_key=api_key, hours=horizon_hours)
    if weather_frame.empty:
        return weather_frame
    weather_frame = weather_frame.copy()
    weather_frame['hour'] = pd.to_datetime(weather_frame['timestamp']).dt.hour
    weather_frame['day_of_week'] = pd.to_datetime(weather_frame['timestamp']).dt.dayofweek
    weather_frame['day_of_year'] = pd.to_datetime(weather_frame['timestamp']).dt.dayofyear
    return weather_frame


def forecast_aqi(model_artifact: dict[str, Any], city: str, horizon_hours: int = 24, api_key: str | None = None) -> pd.DataFrame:
    from backend.services.prediction_service import predict_aqi_dataframe

    forecast_weather = build_forecast_frame(city, horizon_hours=horizon_hours, api_key=api_key)
    if forecast_weather.empty:
        return forecast_weather
    predictions = predict_aqi_dataframe(model_artifact, forecast_weather)
    return predictions
