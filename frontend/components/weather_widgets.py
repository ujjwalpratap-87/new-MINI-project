from __future__ import annotations

import streamlit as st

from backend.utils.aqi import classify_aqi


def render_weather_cards(weather: dict[str, float | str]) -> None:
    cols = st.columns(4)
    items = [
        ('Temperature', f"{weather.get('temperature', 0):.1f}°C"),
        ('Humidity', f"{weather.get('humidity', 0):.0f}%"),
        ('Wind Speed', f"{weather.get('wind_speed', 0):.1f} m/s"),
        ('Pressure', f"{weather.get('pressure', 0):.0f} hPa"),
    ]
    for column, (label, value) in zip(cols, items):
        with column:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>{label}</div>
                    <div class='metric-value'>{value}</div>
                    <div class='metric-delta'>{weather.get('weather_condition', 'Clear')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_alert_banner(predicted_aqi: float) -> None:
    classification = classify_aqi(predicted_aqi)
    if classification.label in {'Poor', 'Very Poor', 'Hazardous'}:
        st.markdown(
            f"<div class='alert-banner'><strong>{classification.label} AQI:</strong> {classification.recommendation}</div>",
            unsafe_allow_html=True,
        )


def render_custom_weather_predictor(model_artifact: dict, city: str) -> None:
    import pandas as pd
    from backend.services.prediction_service import predict_single_city
    from backend.utils.aqi import classify_aqi
    
    st.markdown("<div class='section-title'>Custom Weather Scenario Predictor</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        temp = st.slider('Temperature (°C)', min_value=5.0, max_value=45.0, value=26.0, step=0.1, key='custom_temp')
    with col2:
        humidity = st.slider('Humidity (%)', min_value=10, max_value=100, value=55, step=1, key='custom_humidity')
    with col3:
        wind = st.slider('Wind Speed (m/s)', min_value=0.0, max_value=15.0, value=3.5, step=0.1, key='custom_wind')
    with col4:
        pressure = st.slider('Pressure (hPa)', min_value=980, max_value=1050, value=1013, step=1, key='custom_pressure')
    
    weather_condition = st.selectbox('Weather Condition', ['Clear', 'Clouds', 'Rain', 'Mist', 'Haze', 'Drizzle', 'Thunderstorm'], key='custom_weather')
    
    if st.button('Predict AQI for This Scenario', use_container_width=True, key='custom_predict_btn'):
        custom_payload = {
            'city': city,
            'temperature': float(temp),
            'humidity': float(humidity),
            'wind_speed': float(wind),
            'pressure': float(pressure),
            'weather_condition': weather_condition,
            'timestamp': pd.Timestamp.utcnow(),
        }
        prediction = predict_single_city(model_artifact, custom_payload)
        
        classification = classify_aqi(prediction['predicted_aqi'])
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.success(f"**Predicted AQI**: {prediction['predicted_aqi']:.1f}")
        with col_b:
            st.info(f"**Status**: {classification.label}")
        st.markdown(f"**Recommendation**: {classification.recommendation}")
