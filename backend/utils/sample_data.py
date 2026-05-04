from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
from typing import Iterable

import numpy as np
import pandas as pd

WEATHER_CONDITIONS = ['Clear', 'Clouds', 'Rain', 'Mist', 'Drizzle', 'Thunderstorm', 'Haze']
CITY_FACTORS = {
    'Delhi': 42,
    'Mumbai': 28,
    'Bengaluru': 18,
    'Chennai': 24,
    'Kolkata': 34,
    'Hyderabad': 22,
    'Pune': 20,
    'Ahmedabad': 31,
}

COLUMN_ALIASES = {
    'date': 'timestamp',
    'datetime': 'timestamp',
    'timestamp': 'timestamp',
    'time': 'timestamp',
    'city': 'city',
    'location': 'city',
    'station': 'city',
    'temp': 'temperature',
    'temperature_c': 'temperature',
    'humidity_pct': 'humidity',
    'wind': 'wind_speed',
    'windspeed': 'wind_speed',
    'pressure_hpa': 'pressure',
    'condition': 'weather_condition',
    'weather': 'weather_condition',
    'pm2_5': 'pm25',
    'pm2.5': 'pm25',
    'pm_25': 'pm25',
    'pm10_ugm3': 'pm10',
    'no2_ugm3': 'no2',
    'so2_ugm3': 'so2',
    'co_mgm3': 'co',
    'o3_ugm3': 'o3',
    'aqi_value': 'aqi',
    'air_quality_index': 'aqi',
}

REQUIRED_COLUMNS = ['timestamp', 'city', 'temperature', 'humidity', 'wind_speed', 'pressure', 'weather_condition', 'pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'aqi']


@dataclass(frozen=True)
class SyntheticWeatherSnapshot:
    city: str
    temperature: float
    humidity: float
    wind_speed: float
    pressure: float
    weather_condition: str
    timestamp: pd.Timestamp


def _rng(seed: int = 42) -> np.random.Generator:
    return np.random.default_rng(seed)


def _seasonal_wave(index: np.ndarray, period: float, amplitude: float = 1.0, phase: float = 0.0) -> np.ndarray:
    return amplitude * np.sin((2 * np.pi / period) * index + phase)


def _city_factor(city: str) -> float:
    return CITY_FACTORS.get(city, 26)


def _normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.copy()
    renamed.columns = [str(column).strip().lower().replace(' ', '_') for column in renamed.columns]
    renamed = renamed.rename(columns={column: COLUMN_ALIASES.get(column, column) for column in renamed.columns})
    return renamed


def _derive_missing_features(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    row_count = len(enriched)

    if 'timestamp' in enriched.columns:
        enriched['timestamp'] = pd.to_datetime(enriched['timestamp'], errors='coerce', utc=True)
    else:
        enriched['timestamp'] = pd.date_range(end=pd.Timestamp.utcnow().floor('h'), periods=len(enriched), freq='h')

    if 'city' not in enriched.columns:
        enriched['city'] = 'Unknown'

    if 'weather_condition' not in enriched.columns:
        enriched['weather_condition'] = 'Clear'

    if 'temperature' not in enriched.columns and 'temp' in enriched.columns:
        enriched['temperature'] = enriched['temp']
    if 'humidity' not in enriched.columns and 'humidity_pct' in enriched.columns:
        enriched['humidity'] = enriched['humidity_pct']
    if 'wind_speed' not in enriched.columns and 'wind' in enriched.columns:
        enriched['wind_speed'] = enriched['wind']
    if 'pressure' not in enriched.columns and 'pressure_hpa' in enriched.columns:
        enriched['pressure'] = enriched['pressure_hpa']

    for column, fallback in {
        'temperature': 26.0,
        'humidity': 55.0,
        'wind_speed': 3.5,
        'pressure': 1013.0,
        'pm25': np.nan,
        'pm10': np.nan,
        'no2': np.nan,
        'so2': np.nan,
        'co': np.nan,
        'o3': np.nan,
    }.items():
        if column not in enriched.columns:
            enriched[column] = fallback

    enriched['hour'] = pd.to_datetime(enriched['timestamp'], utc=True, errors='coerce').dt.hour.fillna(0).astype(int)
    enriched['day_of_week'] = pd.to_datetime(enriched['timestamp'], utc=True, errors='coerce').dt.dayofweek.fillna(0).astype(int)
    enriched['day_of_year'] = pd.to_datetime(enriched['timestamp'], utc=True, errors='coerce').dt.dayofyear.fillna(1).astype(int)

    if 'aqi' not in enriched.columns:
        pollutant_columns = [column for column in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'] if column in enriched.columns]
        if pollutant_columns:
            def series_or_default(column: str, default: float) -> pd.Series:
                if column in enriched.columns:
                    return pd.to_numeric(enriched[column], errors='coerce').fillna(default)
                return pd.Series(default, index=enriched.index, dtype='float64')

            weighted = (
                0.30 * series_or_default('pm25', 35.0)
                + 0.22 * series_or_default('pm10', 50.0)
                + 0.18 * series_or_default('no2', 18.0)
                + 0.10 * series_or_default('so2', 12.0)
                + 0.07 * series_or_default('co', 0.8) * 10
                + 0.13 * (180 - series_or_default('o3', 90.0))
            )
            enriched['aqi'] = np.clip(weighted, 0, 500)
        else:
            raise ValueError('aqi column is missing and could not be derived from pollutant columns.')

    return enriched


def generate_sample_historical_data(rows: int = 2500, cities: Iterable[str] | None = None, seed: int = 42) -> pd.DataFrame:
    generator = _rng(seed)
    city_list = list(cities or CITY_FACTORS.keys())
    timestamps = pd.date_range(end=pd.Timestamp.utcnow().floor('h'), periods=rows, freq='h')
    hours = timestamps.hour.to_numpy()
    day_of_year = timestamps.dayofyear.to_numpy()
    day_of_week = timestamps.dayofweek.to_numpy()
    city_choices = generator.choice(city_list, size=rows)

    seasonal = _seasonal_wave(day_of_year, 365.0, amplitude=1.0, phase=-0.6)
    diurnal = _seasonal_wave(hours, 24.0, amplitude=1.0, phase=-0.4)

    temperature = 26 + 9 * seasonal + 5 * diurnal + generator.normal(0, 1.8, rows)
    humidity = np.clip(58 - 14 * seasonal + 16 * _seasonal_wave(hours, 24.0, amplitude=1.0, phase=0.9) + generator.normal(0, 4.0, rows), 18, 100)
    wind_speed = np.clip(3.0 + 1.5 * _seasonal_wave(day_of_year, 30.0, amplitude=1.0, phase=0.1) + generator.normal(0, 0.9, rows), 0.3, 12.0)
    pressure = np.clip(1012 + 5 * _seasonal_wave(day_of_year, 90.0, amplitude=1.0, phase=0.5) + generator.normal(0, 1.6, rows), 990, 1032)

    weather_condition = []
    for h, hum, wind in zip(hours, humidity, wind_speed):
        score = hum + (8 - wind) * 7 + abs(h - 12) * 0.5
        if score > 118:
            weather_condition.append('Rain')
        elif score > 104:
            weather_condition.append('Mist')
        elif score > 96:
            weather_condition.append('Clouds')
        elif score > 90:
            weather_condition.append('Haze')
        else:
            weather_condition.append(generator.choice(['Clear', 'Clouds']))

    weather_condition = np.array(weather_condition)
    condition_impact = np.vectorize({
        'Clear': -6,
        'Clouds': 6,
        'Rain': -12,
        'Mist': 16,
        'Drizzle': 10,
        'Thunderstorm': 20,
        'Haze': 22,
    }.get)(weather_condition)

    city_bias = np.vectorize(_city_factor)(city_choices)
    aqi = (
        35
        + 0.78 * humidity
        - 2.4 * wind_speed
        + 0.55 * (1013 - pressure)
        - 0.28 * temperature
        + 7.5 * seasonal
        + 3.2 * diurnal
        + condition_impact
        + city_bias
        + generator.normal(0, 10.0, rows)
    )
    aqi = np.clip(aqi, 6, 480)

    pm25 = np.clip(0.46 * aqi + generator.normal(0, 5, rows), 4, 320)
    pm10 = np.clip(0.62 * aqi + generator.normal(0, 9, rows), 10, 400)
    no2 = np.clip(0.18 * aqi + generator.normal(0, 3.2, rows), 2, 200)
    so2 = np.clip(0.07 * aqi + generator.normal(0, 2.0, rows), 1, 130)
    co = np.clip(0.015 * aqi + generator.normal(0, 0.15, rows), 0.1, 12)
    o3 = np.clip(90 - 0.11 * aqi + generator.normal(0, 5, rows), 10, 180)

    frame = pd.DataFrame({
        'timestamp': timestamps,
        'city': city_choices,
        'temperature': np.round(temperature, 2),
        'humidity': np.round(humidity, 2),
        'wind_speed': np.round(wind_speed, 2),
        'pressure': np.round(pressure, 2),
        'weather_condition': weather_condition,
        'hour': hours,
        'day_of_week': day_of_week,
        'day_of_year': day_of_year,
        'pm25': np.round(pm25, 2),
        'pm10': np.round(pm10, 2),
        'no2': np.round(no2, 2),
        'so2': np.round(so2, 2),
        'co': np.round(co, 2),
        'o3': np.round(o3, 2),
        'aqi': np.round(aqi, 2),
    })
    return frame.sort_values('timestamp').reset_index(drop=True)


def generate_synthetic_weather_snapshot(city: str, timestamp: pd.Timestamp | None = None, seed: int = 7) -> SyntheticWeatherSnapshot:
    generator = _rng(seed + abs(hash(city)) % 1000)
    ts = timestamp or pd.Timestamp.utcnow()
    hour = ts.hour
    day_of_year = ts.dayofyear
    city_bias = _city_factor(city)

    temperature = float(np.clip(27 + 8 * math.sin(2 * math.pi * (day_of_year / 365.0)) + 4 * math.sin(2 * math.pi * (hour / 24.0)) + generator.normal(0, 1.4), 10, 42))
    humidity = float(np.clip(56 + 18 * math.cos(2 * math.pi * (day_of_year / 365.0)) + generator.normal(0, 5), 20, 100))
    wind_speed = float(np.clip(3.4 + 1.2 * math.cos(2 * math.pi * (hour / 24.0)) + generator.normal(0, 0.8), 0.3, 12))
    pressure = float(np.clip(1011 + 4 * math.sin(2 * math.pi * (day_of_year / 90.0)) + generator.normal(0, 1.3), 990, 1031))

    if humidity > 82:
        weather_condition = 'Mist'
    elif humidity > 72:
        weather_condition = 'Clouds'
    elif wind_speed > 5.5:
        weather_condition = 'Rain'
    else:
        weather_condition = 'Clear'

    if city_bias > 35 and humidity > 65:
        weather_condition = 'Haze'

    return SyntheticWeatherSnapshot(
        city=city,
        temperature=round(temperature, 2),
        humidity=round(humidity, 2),
        wind_speed=round(wind_speed, 2),
        pressure=round(pressure, 2),
        weather_condition=weather_condition,
        timestamp=ts,
    )


def load_real_aqi_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"AQI dataset not found at {path}. Place your real CSV there or set TRAINING_DATA_PATH to the correct file."
        )

    frame = pd.read_csv(path)
    frame = _normalize_columns(frame)
    frame = _derive_missing_features(frame)
    frame = frame.sort_values('timestamp').reset_index(drop=True)
    return frame


def ensure_training_dataset(path: Path, rows: int = 2500) -> pd.DataFrame:
    del rows
    return load_real_aqi_dataset(path)
