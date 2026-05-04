from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

import pandas as pd

from backend.db.models import AQIPredictionRecord
from backend.db.session import get_session
from backend.ml.preprocessing import build_feature_frame
from backend.utils.aqi import classify_aqi


def _prepare_prediction_frame(weather_payload: dict[str, Any] | pd.DataFrame) -> pd.DataFrame:
    if isinstance(weather_payload, pd.DataFrame):
        frame = weather_payload.copy()
    else:
        frame = pd.DataFrame([weather_payload])
    if 'timestamp' not in frame.columns:
        frame['timestamp'] = pd.Timestamp.utcnow()
    return frame


def predict_aqi_dataframe(model_artifact: dict[str, Any], weather_payload: dict[str, Any] | pd.DataFrame) -> pd.DataFrame:
    frame = _prepare_prediction_frame(weather_payload)
    features = build_feature_frame(frame)
    model = model_artifact['model']
    predicted = model.predict(features)
    result = frame.copy()
    result['predicted_aqi'] = predicted
    classifications = result['predicted_aqi'].apply(lambda value: classify_aqi(float(value)))
    result['aqi_label'] = classifications.apply(lambda item: item.label)
    result['aqi_color'] = classifications.apply(lambda item: item.color)
    result['recommendation'] = classifications.apply(lambda item: item.recommendation)
    return result


def predict_single_city(model_artifact: dict[str, Any], weather_payload: dict[str, Any]) -> dict[str, Any]:
    frame = predict_aqi_dataframe(model_artifact, weather_payload)
    row = frame.iloc[0].to_dict()
    return row


def store_prediction(record: dict[str, Any]) -> None:
    with get_session() as session:
        db_record = AQIPredictionRecord(
            city=record.get('city', 'Unknown'),
            timestamp=pd.to_datetime(record.get('timestamp', pd.Timestamp.utcnow())).to_pydatetime(),
            temperature=float(record.get('temperature', 0.0)),
            humidity=float(record.get('humidity', 0.0)),
            wind_speed=float(record.get('wind_speed', 0.0)),
            pressure=float(record.get('pressure', 0.0)),
            weather_condition=str(record.get('weather_condition', 'Clear')),
            predicted_aqi=float(record.get('predicted_aqi', 0.0)),
            actual_aqi=record.get('actual_aqi'),
            model_name=str(record.get('model_name', 'Unknown')),
            health_label=str(record.get('aqi_label', 'Unknown')),
            recommendation=str(record.get('recommendation', '')),
        )
        session.add(db_record)


def fetch_recent_predictions(limit: int = 100) -> list[dict[str, Any]]:
    from sqlalchemy import select

    with get_session() as session:
        rows = session.execute(select(AQIPredictionRecord).order_by(AQIPredictionRecord.timestamp.desc()).limit(limit)).scalars().all()
        return [
            {
                'id': row.id,
                'city': row.city,
                'timestamp': row.timestamp,
                'temperature': row.temperature,
                'humidity': row.humidity,
                'wind_speed': row.wind_speed,
                'pressure': row.pressure,
                'weather_condition': row.weather_condition,
                'predicted_aqi': row.predicted_aqi,
                'actual_aqi': row.actual_aqi,
                'model_name': row.model_name,
                'health_label': row.health_label,
                'recommendation': row.recommendation,
            }
            for row in rows
        ]
