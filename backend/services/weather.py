from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd
import requests

from backend.core.config import settings
from backend.utils.sample_data import SyntheticWeatherSnapshot, generate_synthetic_weather_snapshot

OPENWEATHER_CURRENT_URL = 'https://api.openweathermap.org/data/2.5/weather'
OPENWEATHER_FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'


class WeatherAPIError(RuntimeError):
    pass


def _normalize_condition(raw_condition: str | None) -> str:
    condition = (raw_condition or 'Clear').strip().title()
    if condition not in {'Clear', 'Clouds', 'Rain', 'Mist', 'Drizzle', 'Thunderstorm', 'Haze', 'Smoke'}:
        return 'Clouds'
    return 'Haze' if condition == 'Smoke' else condition


def fetch_current_weather(city: str, api_key: str | None = None) -> dict[str, Any]:
    api_key = api_key or settings.openweather_api_key
    if not api_key:
        snapshot = generate_synthetic_weather_snapshot(city)
        return {**asdict(snapshot), 'source': 'synthetic'}

    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    response = requests.get(OPENWEATHER_CURRENT_URL, params=params, timeout=15)
    if response.status_code != 200:
        snapshot = generate_synthetic_weather_snapshot(city)
        return {**asdict(snapshot), 'source': f'synthetic_fallback:{response.status_code}'}

    payload = response.json()
    weather = payload.get('weather', [{}])[0]
    main = payload.get('main', {})
    wind = payload.get('wind', {})
    snapshot = {
        'city': payload.get('name', city),
        'temperature': float(main.get('temp', 0.0)),
        'humidity': float(main.get('humidity', 0.0)),
        'wind_speed': float(wind.get('speed', 0.0)),
        'pressure': float(main.get('pressure', 0.0)),
        'weather_condition': _normalize_condition(weather.get('main')),
        'timestamp': pd.Timestamp.utcnow(),
        'source': 'openweather',
    }
    return snapshot


def fetch_weather_forecast(city: str, api_key: str | None = None, hours: int = 24) -> pd.DataFrame:
    api_key = api_key or settings.openweather_api_key
    if not api_key:
        base = pd.Timestamp.utcnow().floor('h')
        rows = []
        for offset in range(hours):
            snapshot = generate_synthetic_weather_snapshot(city, timestamp=base + pd.Timedelta(hours=offset), seed=offset + 11)
            rows.append(asdict(snapshot))
        return pd.DataFrame(rows)

    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    response = requests.get(OPENWEATHER_FORECAST_URL, params=params, timeout=15)
    if response.status_code != 200:
        return fetch_weather_forecast(city, api_key=None, hours=hours)

    payload = response.json()
    rows: list[dict[str, Any]] = []
    for item in payload.get('list', [])[: max(1, hours // 3)]:
        rows.append({
            'city': payload.get('city', {}).get('name', city),
            'temperature': float(item.get('main', {}).get('temp', 0.0)),
            'humidity': float(item.get('main', {}).get('humidity', 0.0)),
            'wind_speed': float(item.get('wind', {}).get('speed', 0.0)),
            'pressure': float(item.get('main', {}).get('pressure', 0.0)),
            'weather_condition': _normalize_condition(item.get('weather', [{}])[0].get('main')),
            'timestamp': pd.to_datetime(item.get('dt_txt')),
            'source': 'openweather',
        })
    frame = pd.DataFrame(rows)
    if frame.empty:
        return fetch_weather_forecast(city, api_key=None, hours=hours)
    return frame
