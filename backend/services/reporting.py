from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.utils.aqi import classify_aqi


def build_report_payload(summary: dict[str, Any], latest_prediction: dict[str, Any]) -> dict[str, Any]:
    classification = classify_aqi(float(latest_prediction.get('predicted_aqi', 0)))
    return {
        'summary': summary,
        'latest_prediction': latest_prediction,
        'classification': classification,
    }


def generate_pdf_report(payload: dict[str, Any]) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=28, leftMargin=28, topMargin=28, bottomMargin=28)
    styles = getSampleStyleSheet()
    story = [
        Paragraph('AI-Based Air Pollution Prediction System', styles['Title']),
        Spacer(1, 12),
        Paragraph('Executive Summary', styles['Heading2']),
        Paragraph(f"Best AQI status: {payload['classification'].label}", styles['BodyText']),
        Spacer(1, 12),
    ]

    summary_table = Table([
        ['Metric', 'Value'],
        ['Records', payload['summary'].get('records', 0)],
        ['Average AQI', f"{payload['summary'].get('average_aqi', 0):.2f}"],
        ['Average Temperature', f"{payload['summary'].get('average_temperature', 0):.2f}"],
        ['Average Humidity', f"{payload['summary'].get('average_humidity', 0):.2f}"],
    ])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#374151')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 16))

    prediction_rows = [[key, value] for key, value in payload['latest_prediction'].items() if key in {'city', 'predicted_aqi', 'aqi_label', 'recommendation', 'weather_condition'}]
    prediction_table = Table([['Field', 'Value']] + prediction_rows)
    prediction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#374151')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eef2ff')),
    ]))
    story.append(Paragraph('Latest Prediction', styles['Heading2']))
    story.append(prediction_table)
    document.build(story)
    return buffer.getvalue()
