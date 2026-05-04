from __future__ import annotations

import streamlit as st

from backend.utils.aqi import classify_aqi


def render_kpi_cards(aqi_value: float, temperature: float, humidity: float, model_name: str, records: int) -> None:
    classification = classify_aqi(aqi_value)
    cols = st.columns(5)
    metrics = [
        ('AQI', f'{aqi_value:.1f}', classification.label),
        ('Status', classification.label, classification.recommendation),
        ('Temp', f'{temperature:.1f}°C', 'Current weather'),
        ('Humidity', f'{humidity:.0f}%', 'Atmospheric moisture'),
        ('Best Model', model_name, f'{records:,} training rows'),
    ]
    for column, (label, value, note) in zip(cols, metrics):
        with column:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>{label}</div>
                    <div class='metric-value'>{value}</div>
                    <div class='metric-delta'>{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
