from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / '.env')


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv('APP_NAME', 'AI-Based Air Pollution Prediction System')
    weather_provider: str = os.getenv('WEATHER_PROVIDER', 'openweather')
    openweather_api_key: str = os.getenv('OPENWEATHER_API_KEY', '')
    database_url: str = os.getenv('DATABASE_URL', f"sqlite:///{(BASE_DIR / 'data' / 'aqi.db').as_posix()}")
    model_artifact_path: Path = Path(os.getenv('MODEL_ARTIFACT_PATH', BASE_DIR / 'artifacts' / 'best_model.joblib'))
    metrics_path: Path = Path(os.getenv('MODEL_METRICS_PATH', BASE_DIR / 'artifacts' / 'model_metrics.json'))
    training_data_path: Path = Path(os.getenv('TRAINING_DATA_PATH', BASE_DIR / 'data' / 'raw' / 'aqi.csv'))
    processed_data_path: Path = Path(os.getenv('PROCESSED_DATA_PATH', BASE_DIR / 'data' / 'processed' / 'aqi_processed.csv'))
    artifacts_dir: Path = BASE_DIR / 'artifacts'
    raw_data_dir: Path = BASE_DIR / 'data' / 'raw'
    processed_data_dir: Path = BASE_DIR / 'data' / 'processed'
    api_host: str = os.getenv('API_HOST', '0.0.0.0')
    api_port: int = int(os.getenv('API_PORT', '8000'))
    streamlit_port: int = int(os.getenv('STREAMLIT_PORT', '8501'))
    default_city: str = os.getenv('DEFAULT_CITY', 'Delhi')

    def ensure_directories(self) -> None:
        for path in (self.artifacts_dir, self.raw_data_dir, self.processed_data_dir):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
