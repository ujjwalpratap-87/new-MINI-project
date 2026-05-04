from __future__ import annotations

from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from backend.core.config import settings
from backend.db.session import init_database
from backend.ml.forecast import forecast_aqi
from backend.ml.train import load_or_train_model, train_best_model
from backend.services.data_service import compute_summary_statistics, load_historical_data
from backend.services.prediction_service import predict_single_city, store_prediction
from backend.services.reporting import build_report_payload, generate_pdf_report
from backend.services.weather import fetch_current_weather
from backend.utils.aqi import classify_aqi
from backend.utils.plotting import create_forecast_chart
from frontend.components.charts import render_dashboard_charts
from frontend.components.kpis import render_kpi_cards
from frontend.components.sidebar import render_sidebar
from frontend.components.weather_widgets import render_alert_banner, render_weather_cards, render_custom_weather_predictor
from frontend.styles import apply_dashboard_style

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:  # pragma: no cover - optional dependency
    st_autorefresh = None

st.set_page_config(page_title=settings.app_name, page_icon='🌍', layout='wide', initial_sidebar_state='expanded')
init_database()

@st.cache_data(ttl=900, show_spinner=False)
def load_data() -> pd.DataFrame:
    return load_historical_data()


@st.cache_resource(show_spinner=False)
def load_model(force_retrain: bool = False):
    if force_retrain:
        return train_best_model()
    return load_or_train_model()


historical_frame = load_data()
if historical_frame.empty:
    st.error(f"No AQI records found in {settings.training_data_path}. Add your real CSV there and rerun the app.")
    st.stop()

model_artifact = load_model()
summary = compute_summary_statistics(historical_frame)
city, section, dark_mode, auto_refresh = render_sidebar(settings.default_city)
apply_dashboard_style(dark_mode=dark_mode)

if auto_refresh and st_autorefresh is not None:
    st_autorefresh(interval=300000, limit=None, key='weather_autorefresh')

st.markdown(
    """
    <div class='hero-banner'>
        <div class='soft-chip'>Live weather intelligence</div>
        <div class='soft-chip'>Best-model auto selection</div>
        <div class='soft-chip'>Historical + forecast analytics</div>
        <div class='brand-title' style='margin-top: 0.6rem;'>AI-Based Air Pollution Prediction System</div>
        <div class='brand-subtitle'>Production-style environmental analytics for AQI monitoring, prediction, forecasting, and operational reporting.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write('')

with st.spinner('Loading live weather intelligence and model outputs...'):
    weather_snapshot = fetch_current_weather(city)
    prediction_payload = dict(weather_snapshot)
    prediction_payload['city'] = city
    prediction_result = predict_single_city(model_artifact, prediction_payload)
    prediction_result['model_name'] = model_artifact['model_name']
    forecast_frame = forecast_aqi(model_artifact, city, horizon_hours=24)

prediction_cache_key = f"{city}:{weather_snapshot.get('timestamp')}:{weather_snapshot.get('source', 'unknown')}"
if st.session_state.get('last_saved_prediction_key') != prediction_cache_key:
    store_prediction(prediction_result)
    st.session_state['last_saved_prediction_key'] = prediction_cache_key

latest_aqi = float(prediction_result['predicted_aqi'])
classification = classify_aqi(latest_aqi)

render_kpi_cards(latest_aqi, float(prediction_result['temperature']), float(prediction_result['humidity']), model_artifact['model_name'], summary['records'])
render_alert_banner(latest_aqi)
render_weather_cards(prediction_result)

st.write('')

left, right = st.columns([1.2, 0.8])
with left:
    st.markdown("<div class='section-title'>Current Prediction</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='dashboard-shell'>
            <div class='soft-chip'>City: {prediction_result['city']}</div>
            <div class='soft-chip'>Weather: {prediction_result['weather_condition']}</div>
            <div class='soft-chip'>Source: {weather_snapshot.get('source', 'unknown')}</div>
            <p class='small-muted'>Predicted AQI is automatically classified into health categories with operational guidance for the selected city.</p>
            <h2 style='font-family: Sora, sans-serif; margin-bottom: 0.2rem;'>AQI {latest_aqi:.1f}</h2>
            <p style='color: {classification.color}; font-weight: 700; margin-bottom: 0.35rem;'>{classification.label}</p>
            <p class='small-muted'>{classification.recommendation}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    st.markdown("<div class='section-title'>Operational Actions</div>", unsafe_allow_html=True)
    payload = build_report_payload(summary, prediction_result)
    pdf_bytes = generate_pdf_report(payload)
    st.download_button('Download PDF Report', data=pdf_bytes, file_name='aqi_report.pdf', mime='application/pdf', use_container_width=True)
    csv_bytes = historical_frame.to_csv(index=False).encode('utf-8')
    st.download_button('Download Historical CSV', data=csv_bytes, file_name='historical_aqi.csv', mime='text/csv', use_container_width=True)
    st.caption('Reports and exports are generated locally and do not require external services.')

if section == 'Overview':
    render_dashboard_charts(historical_frame, forecast_frame, latest_aqi)
    st.markdown("<div class='section-title'>Historical Data</div>", unsafe_allow_html=True)
    st.dataframe(historical_frame.tail(100), use_container_width=True, height=320)
    st.divider()
    render_custom_weather_predictor(model_artifact, city)
    st.divider()
    render_custom_weather_predictor(model_artifact, city)

elif section == 'Forecast':
    st.markdown("<div class='section-title'>24-Hour Forecast</div>", unsafe_allow_html=True)
    st.plotly_chart(create_forecast_chart(forecast_frame), use_container_width=True)
    st.dataframe(forecast_frame[['timestamp', 'temperature', 'humidity', 'wind_speed', 'pressure', 'weather_condition', 'predicted_aqi']], use_container_width=True, height=340)

elif section == 'Data Lab':
    st.markdown("<div class='section-title'>Analytics Workspace</div>", unsafe_allow_html=True)
    city_frame = historical_frame[historical_frame['city'] == city] if 'city' in historical_frame.columns else historical_frame
    st.dataframe(city_frame.head(200), use_container_width=True, height=340)
    st.bar_chart(city_frame.groupby('weather_condition')['aqi'].mean())
    city_coordinates = {
        'Delhi': (28.6139, 77.2090),
        'Mumbai': (19.0760, 72.8777),
        'Bengaluru': (12.9716, 77.5946),
        'Chennai': (13.0827, 80.2707),
        'Kolkata': (22.5726, 88.3639),
        'Hyderabad': (17.3850, 78.4867),
        'Pune': (18.5204, 73.8567),
        'Ahmedabad': (23.0225, 72.5714),
    }
    geo_frame = historical_frame.groupby('city', as_index=False)['aqi'].mean().rename(columns={'aqi': 'average_aqi'})
    geo_frame['lat'] = geo_frame['city'].map(lambda value: city_coordinates.get(value, (20.0, 78.0))[0])
    geo_frame['lon'] = geo_frame['city'].map(lambda value: city_coordinates.get(value, (20.0, 78.0))[1])
    st.plotly_chart(
        px.scatter_geo(
            geo_frame,
            lat='lat',
            lon='lon',
            size='average_aqi',
            color='average_aqi',
            hover_name='city',
            projection='natural earth',
            title='AQI Geo Intelligence',
            color_continuous_scale='Turbo',
            template='plotly_dark',
        ),
        use_container_width=True,
    )

elif section == 'Model Lab':
    st.markdown("<div class='section-title'>Model Intelligence</div>", unsafe_allow_html=True)
    metrics = load_model()['metrics']
    leaderboard = pd.DataFrame(load_model()['leaderboard'])
    st.json(metrics)
    st.dataframe(leaderboard, use_container_width=True)
    if st.button('Retrain Model'):
        with st.spinner('Retraining and re-evaluating models...'):
            st.cache_resource.clear()
            updated = train_best_model()
            st.success(f"Best model updated to {updated['model_name']}")
            st.rerun()

st.caption('Designed as a startup-grade analytics platform with modular backend services, live weather integration, and operational reporting.')
