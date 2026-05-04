from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
from fastapi import FastAPI

from backend.api.schemas import PredictionRequest, PredictionResponse, TrainResponse, WeatherRequest
from backend.core.config import settings
from backend.db.session import init_database
from backend.ml.train import load_or_train_model, train_best_model
from backend.services.prediction_service import predict_single_city, store_prediction
from backend.services.weather import fetch_current_weather
from backend.utils.aqi import classify_aqi

app = FastAPI(title=settings.app_name, version='1.0.0')


@app.on_event('startup')
def on_startup() -> None:
    init_database()
    load_or_train_model(force_retrain=False)


@app.get('/health')
def health_check() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/weather/current')
def current_weather(request: WeatherRequest) -> dict[str, Any]:
    return fetch_current_weather(request.city)


@app.post('/predict', response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    model_artifact = load_or_train_model(force_retrain=False)
    weather_payload = fetch_current_weather(request.city)
    for field in ('temperature', 'humidity', 'wind_speed', 'pressure', 'weather_condition'):
        value = getattr(request, field)
        if value is not None:
            weather_payload[field] = value
    weather_payload['timestamp'] = weather_payload.get('timestamp', datetime.utcnow())
    prediction = predict_single_city(model_artifact, weather_payload)
    prediction['model_name'] = model_artifact['model_name']
    prediction['source'] = weather_payload.get('source')
    store_prediction(prediction)
    classification = classify_aqi(prediction['predicted_aqi'])
    return PredictionResponse(
        city=str(prediction.get('city', request.city)),
        timestamp=pd.to_datetime(prediction.get('timestamp', datetime.utcnow())).to_pydatetime(),
        temperature=float(prediction['temperature']),
        humidity=float(prediction['humidity']),
        wind_speed=float(prediction['wind_speed']),
        pressure=float(prediction['pressure']),
        weather_condition=str(prediction['weather_condition']),
        predicted_aqi=float(prediction['predicted_aqi']),
        aqi_label=classification.label,
        recommendation=classification.recommendation,
        model_name=str(prediction['model_name']),
        source=str(prediction.get('source', 'unknown')),
    )


@app.post('/train', response_model=TrainResponse)
def train() -> TrainResponse:
    artifact = train_best_model()
    return TrainResponse(best_model=artifact['model_name'], metrics=artifact['metrics'], leaderboard=artifact['leaderboard'])


@app.get('/predictions/recent')
def recent_predictions(limit: int = 50) -> list[dict[str, Any]]:
    from backend.services.prediction_service import fetch_recent_predictions

    return fetch_recent_predictions(limit=limit)
