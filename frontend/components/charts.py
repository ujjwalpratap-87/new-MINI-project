from __future__ import annotations

import streamlit as st

from backend.utils.plotting import (
    create_aqi_distribution_pie,
    create_aqi_gauge,
    create_correlation_heatmap,
    create_forecast_chart,
    create_pollutant_bar_chart,
    create_trend_chart,
)


def render_dashboard_charts(historical_frame, forecast_frame, latest_aqi: float) -> None:
    st.markdown("<div class='section-title'>Performance Overview</div>", unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9])
    with left:
        st.plotly_chart(create_aqi_gauge(latest_aqi), use_container_width=True)
    with right:
        st.plotly_chart(create_aqi_distribution_pie(historical_frame), use_container_width=True)

    row_one_left, row_one_right = st.columns(2)
    with row_one_left:
        st.plotly_chart(create_trend_chart(historical_frame, title='Historical AQI Trend'), use_container_width=True)
    with row_one_right:
        st.plotly_chart(create_pollutant_bar_chart(historical_frame), use_container_width=True)

    row_two_left, row_two_right = st.columns(2)
    with row_two_left:
        fig = create_correlation_heatmap(historical_frame)
        st.pyplot(fig, use_container_width=True, clear_figure=True)
    with row_two_right:
        if forecast_frame is not None and not forecast_frame.empty:
            st.plotly_chart(create_forecast_chart(forecast_frame), use_container_width=True)
        else:
            st.info('Forecast data will appear once the model is trained and weather forecast data is available.')
