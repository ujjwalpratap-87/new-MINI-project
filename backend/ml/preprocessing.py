from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = ['temperature', 'humidity', 'wind_speed', 'pressure', 'pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'hour', 'day_of_week', 'day_of_year']
CATEGORICAL_FEATURES = ['weather_condition']
TARGET_COLUMN = 'aqi'


def add_temporal_features(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    if 'timestamp' in enriched.columns:
        timestamp = pd.to_datetime(enriched['timestamp'], utc=True, errors='coerce')
        enriched['hour'] = timestamp.dt.hour.fillna(0).astype(int)
        enriched['day_of_week'] = timestamp.dt.dayofweek.fillna(0).astype(int)
        enriched['day_of_year'] = timestamp.dt.dayofyear.fillna(1).astype(int)
    else:
        if 'hour' not in enriched.columns:
            enriched['hour'] = 12
        if 'day_of_week' not in enriched.columns:
            enriched['day_of_week'] = 2
        if 'day_of_year' not in enriched.columns:
            enriched['day_of_year'] = 180

    pollutant_defaults = {
        'pm25': 35.0,
        'pm10': 50.0,
        'no2': 18.0,
        'so2': 12.0,
        'co': 0.8,
        'o3': 90.0,
    }
    for column, default_value in pollutant_defaults.items():
        if column not in enriched.columns:
            enriched[column] = default_value
        enriched[column] = pd.to_numeric(enriched[column], errors='coerce').fillna(default_value)

    if 'temperature' in enriched.columns:
        enriched['temperature'] = pd.to_numeric(enriched['temperature'], errors='coerce').fillna(26.0)
    if 'humidity' in enriched.columns:
        enriched['humidity'] = pd.to_numeric(enriched['humidity'], errors='coerce').fillna(55.0)
    if 'wind_speed' in enriched.columns:
        enriched['wind_speed'] = pd.to_numeric(enriched['wind_speed'], errors='coerce').fillna(3.5)
    if 'pressure' in enriched.columns:
        enriched['pressure'] = pd.to_numeric(enriched['pressure'], errors='coerce').fillna(1013.0)
    return enriched


def select_training_features(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = add_temporal_features(frame)
    missing = [column for column in NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET_COLUMN] if column not in enriched.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    return enriched[NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET_COLUMN]]


def build_feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = add_temporal_features(frame)
    required = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    for column in required:
        if column not in enriched.columns:
            raise ValueError(f'Missing required feature column: {column}')
    return enriched[required]


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ])
    return ColumnTransformer([
        ('numeric', numeric_pipeline, NUMERIC_FEATURES),
        ('categorical', categorical_pipeline, CATEGORICAL_FEATURES),
    ])
