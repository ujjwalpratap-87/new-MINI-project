from __future__ import annotations

import streamlit as st


DARK_MODE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@500;600;700&display=swap');

:root {
    --bg: #060a13;
    --panel: rgba(10, 15, 28, 0.82);
    --panel-strong: rgba(12, 18, 33, 0.96);
    --border: rgba(255, 255, 255, 0.08);
    --text: #e8edf7;
    --muted: #8e9ab3;
    --accent: #69d2ff;
    --accent-2: #5ce7a7;
    --danger: #ff6a7a;
    --warning: #ffbf69;
    --shadow: 0 18px 48px rgba(0, 0, 0, 0.34);
}
"""

LIGHT_MODE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@500;600;700&display=swap');

:root {
    --bg: #f8f9fa;
    --panel: rgba(255, 255, 255, 0.95);
    --panel-strong: rgba(255, 255, 255, 0.98);
    --border: rgba(0, 0, 0, 0.10);
    --text: #1a1a1a;
    --muted: #666666;
    --accent: #0066cc;
    --accent-2: #00aa55;
    --danger: #cc0000;
    --warning: #ff9900;
    --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
"""

DASHBOARD_CSS_BASE = """
<style>

html, body, [class*='css'] {
    font-family: 'Inter', sans-serif;
    color: var(--text);
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(105, 210, 255, 0.12), transparent 24%),
        radial-gradient(circle at top right, rgba(92, 231, 167, 0.10), transparent 28%),
        linear-gradient(180deg, #05070d 0%, #090d18 44%, #060a13 100%);
}

section[data-testid='stSidebar'] {
    background: linear-gradient(180deg, rgba(8, 12, 22, 0.98), rgba(6, 10, 19, 0.98));
    border-right: 1px solid var(--border);
}

main .block-container {
    padding-top: 1.25rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

.brand-title {
    font-family: 'Sora', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.05;
    margin-bottom: 0.4rem;
}

.brand-subtitle {
    color: var(--muted);
    font-size: 0.96rem;
    line-height: 1.5;
    max-width: 760px;
}

.dashboard-shell {
    border: 1px solid var(--border);
    border-radius: 24px;
    background: linear-gradient(180deg, rgba(12, 18, 33, 0.88), rgba(8, 12, 22, 0.94));
    box-shadow: var(--shadow);
    padding: 1.1rem;
}

.metric-card {
    background: linear-gradient(180deg, rgba(14, 20, 38, 0.95), rgba(10, 15, 28, 0.95));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow);
    min-height: 120px;
}

.metric-label {
    color: var(--muted);
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    margin-bottom: 0.55rem;
}

.metric-value {
    font-family: 'Sora', sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: -0.03em;
}

.metric-delta {
    margin-top: 0.45rem;
    font-size: 0.9rem;
    color: var(--muted);
}

.card-grid {
    display: grid;
    gap: 1rem;
}

.hero-banner {
    border-radius: 24px;
    border: 1px solid var(--border);
    background: linear-gradient(135deg, rgba(105, 210, 255, 0.14), rgba(92, 231, 167, 0.08) 56%, rgba(10, 15, 28, 0.9));
    padding: 1.2rem 1.4rem;
    box-shadow: var(--shadow);
}

.soft-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    border: 1px solid var(--border);
    background: rgba(255, 255, 255, 0.03);
    color: var(--text);
    padding: 0.38rem 0.72rem;
    border-radius: 999px;
    font-size: 0.82rem;
    margin-right: 0.45rem;
    margin-bottom: 0.45rem;
}

.alert-banner {
    border-radius: 18px;
    border: 1px solid rgba(255, 106, 122, 0.28);
    background: rgba(255, 106, 122, 0.08);
    color: #ffd2d8;
    padding: 0.9rem 1rem;
}

.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 0.85rem;
}

.small-muted {
    color: var(--muted);
    font-size: 0.88rem;
}

.stButton > button {
    border: 1px solid rgba(255, 255, 255, 0.10);
    background: linear-gradient(135deg, rgba(105, 210, 255, 0.20), rgba(92, 231, 167, 0.14));
    color: var(--text);
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-weight: 600;
    transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(105, 210, 255, 0.28);
}

.stDataFrame, .stPlotlyChart, .stMetric, .stDownloadButton {
    border-radius: 16px;
}

@media (max-width: 768px) {
    main .block-container {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }

    .brand-title {
        font-size: 1.6rem;
    }
}
</style>
"""


def apply_dashboard_style(dark_mode: bool = True) -> None:
    theme_css = DARK_MODE_CSS if dark_mode else LIGHT_MODE_CSS
    full_css = theme_css + DASHBOARD_CSS_BASE
    st.markdown(full_css, unsafe_allow_html=True)
