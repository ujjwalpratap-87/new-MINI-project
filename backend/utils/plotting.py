from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

from backend.utils.aqi import classify_aqi

DARK_TEMPLATE = 'plotly_dark'


def create_aqi_gauge(aqi_value: float) -> go.Figure:
    classification = classify_aqi(aqi_value)
    fig = go.Figure(
        go.Indicator(
            mode='gauge+number+delta',
            value=float(aqi_value),
            number={'suffix': ' AQI'},
            title={'text': f'AQI - {classification.label}'},
            delta={'reference': 100},
            gauge={
                'axis': {'range': [0, 500]},
                'bar': {'color': classification.color},
                'steps': [
                    {'range': [0, 50], 'color': '#1f3b2d'},
                    {'range': [50, 100], 'color': '#4a4310'},
                    {'range': [100, 150], 'color': '#5a3514'},
                    {'range': [150, 200], 'color': '#5b1b1b'},
                    {'range': [200, 500], 'color': '#35173f'},
                ],
            },
        )
    )
    fig.update_layout(template=DARK_TEMPLATE, height=330, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig


def create_trend_chart(frame: pd.DataFrame, title: str = 'AQI Trend') -> go.Figure:
    fig = px.line(frame, x='timestamp', y='aqi', color='city' if 'city' in frame.columns else None, markers=True, title=title, template=DARK_TEMPLATE)
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def create_pollutant_bar_chart(frame: pd.DataFrame) -> go.Figure:
    pollutants = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']
    averages = frame[pollutants].mean().reset_index()
    averages.columns = ['pollutant', 'value']
    fig = px.bar(averages, x='pollutant', y='value', color='pollutant', title='Pollutant Comparison', template=DARK_TEMPLATE)
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
    return fig


def create_aqi_distribution_pie(frame: pd.DataFrame) -> go.Figure:
    labels = frame['aqi'].apply(lambda value: classify_aqi(value).label).value_counts().reset_index()
    labels.columns = ['category', 'count']
    fig = px.pie(labels, names='category', values='count', title='AQI Category Distribution', template=DARK_TEMPLATE)
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def create_correlation_heatmap(frame: pd.DataFrame) -> plt.Figure:
    numeric_frame = frame.select_dtypes(include='number')
    correlation = numeric_frame.corr(numeric_only=True)
    figure, axis = plt.subplots(figsize=(10, 7), facecolor='#0d1117')
    axis.set_facecolor('#0d1117')
    sns.heatmap(correlation, cmap='mako', annot=False, cbar=True, square=False, ax=axis)
    axis.set_title('Correlation Heatmap', color='white', fontsize=14, pad=14)
    axis.tick_params(colors='white')
    for spine in axis.spines.values():
        spine.set_color('#2d333b')
    figure.tight_layout()
    return figure


def create_forecast_chart(forecast_frame: pd.DataFrame) -> go.Figure:
    fig = px.line(forecast_frame, x='timestamp', y='predicted_aqi', title='24-Hour AQI Forecast', markers=True, template=DARK_TEMPLATE)
    fig.update_traces(line=dict(width=3))
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=50, b=10))
    return fig
