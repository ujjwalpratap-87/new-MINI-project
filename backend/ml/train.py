from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from backend.core.config import settings
from backend.ml.evaluate import compare_models
from backend.utils.sample_data import ensure_training_dataset


class TrainingError(RuntimeError):
    pass


def prepare_training_frame(dataset_path: Path | None = None) -> pd.DataFrame:
    path = dataset_path or settings.training_data_path
    frame = ensure_training_dataset(path)
    frame = frame.sort_values('timestamp').reset_index(drop=True)
    processed_path = settings.processed_data_path
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(processed_path, index=False)
    return frame


def train_best_model(dataset_path: Path | None = None, random_state: int = 42) -> dict[str, Any]:
    frame = prepare_training_frame(dataset_path)
    best_result, leaderboard = compare_models(frame, random_state=random_state)
    artifact = {
        'model': best_result.pipeline,
        'model_name': best_result.name,
        'metrics': best_result.metrics,
        'leaderboard': leaderboard,
        'trained_rows': int(len(frame)),
        'feature_columns': ['temperature', 'humidity', 'wind_speed', 'pressure', 'hour', 'day_of_week', 'day_of_year', 'weather_condition'],
    }

    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, settings.model_artifact_path)
    with open(settings.metrics_path, 'w', encoding='utf-8') as handle:
        json.dump({'best_model': best_result.name, 'metrics': best_result.metrics, 'leaderboard': leaderboard}, handle, indent=2)
    return artifact


def load_or_train_model(force_retrain: bool = False) -> dict[str, Any]:
    if settings.model_artifact_path.exists() and not force_retrain:
        return joblib.load(settings.model_artifact_path)
    return train_best_model()
