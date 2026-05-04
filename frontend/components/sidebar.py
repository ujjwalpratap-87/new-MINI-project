from __future__ import annotations

from typing import Literal

import streamlit as st

NAV_OPTIONS = ['Overview', 'Forecast', 'Data Lab', 'Model Lab']


def render_sidebar(default_city: str) -> tuple[str, str, bool, bool]:
    with st.sidebar:
        st.markdown("<div class='brand-title'>AQI Intelligence</div>", unsafe_allow_html=True)
        st.markdown("<div class='brand-subtitle'>Startup-grade air quality intelligence with live weather, model comparison, and operational analytics.</div>", unsafe_allow_html=True)
        st.markdown('---')
        city = st.text_input('City', value=default_city, help='Search any city for live AQI prediction')
        section = st.radio('Navigation', NAV_OPTIONS, index=0)
        dark_mode = st.toggle('Dark Mode', value=True)
        auto_refresh = st.toggle('Auto-refresh weather', value=False)
        st.caption('API key is read from .env and never exposed in the UI.')
        return city.strip() or default_city, section, dark_mode, auto_refresh
