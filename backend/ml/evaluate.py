from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.base import RegressorMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover - optional dependency
    XGBRegressor = None

from backend.ml.preprocessing import build_preprocessor


@dataclass
class ModelResult:
    name: str
    pipeline: Pipeline
    metrics: dict[str, float]


def build_candidate_models(random_state: int = 42) -> dict[str, RegressorMixin]:
    models: dict[str, RegressorMixin] = {
        'LinearRegression': LinearRegression(),
        'RandomForestRegressor': RandomForestRegressor(n_estimators=250, random_state=random_state, n_jobs=-1),
    }
    if XGBRegressor is not None:
        models['XGBoost'] = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=random_state,
            objective='reg:squarederror',
        )
    return models


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    mse = mean_squared_error(y_true, y_pred)
    return {
        'mae': float(mean_absolute_error(y_true, y_pred)),
        'rmse': float(np.sqrt(mse)),
        'r2': float(r2_score(y_true, y_pred)),
    }


def train_test_evaluate(frame, target_column: str = 'aqi', random_state: int = 42) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    from backend.ml.preprocessing import build_feature_frame, select_training_features

    training = select_training_features(frame)
    X = build_feature_frame(training)
    y = training[target_column].to_numpy()
    return train_test_split(X, y, test_size=0.2, random_state=random_state)


def compare_models(frame, random_state: int = 42) -> tuple[ModelResult, list[dict[str, Any]]]:
    from backend.ml.preprocessing import build_feature_frame, select_training_features

    selected = select_training_features(frame)
    X = build_feature_frame(selected)
    y = selected['aqi'].to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)
    preprocessor = build_preprocessor()

    results: list[ModelResult] = []
    for model_name, estimator in build_candidate_models(random_state=random_state).items():
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', estimator),
        ])
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        metrics = evaluate_predictions(y_test, predictions)
        results.append(ModelResult(name=model_name, pipeline=pipeline, metrics=metrics))

    ranked = sorted(results, key=lambda item: (item.metrics['rmse'], item.metrics['mae']))
    leaderboard = [{'model': result.name, **result.metrics} for result in ranked]
    return ranked[0], leaderboard
