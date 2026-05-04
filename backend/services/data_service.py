from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from backend.core.config import settings
from backend.utils.sample_data import ensure_training_dataset


def load_historical_data(path: Path | None = None) -> pd.DataFrame:
    target_path = path or settings.training_data_path
    frame = ensure_training_dataset(target_path)
    frame['timestamp'] = pd.to_datetime(frame['timestamp'])
    return frame


def compute_summary_statistics(frame: pd.DataFrame) -> dict[str, Any]:
    summary = {
        'records': int(len(frame)),
        'average_aqi': float(frame['aqi'].mean()),
        'max_aqi': float(frame['aqi'].max()),
        'min_aqi': float(frame['aqi'].min()),
        'average_temperature': float(frame['temperature'].mean()),
        'average_humidity': float(frame['humidity'].mean()),
    }
    return summary
