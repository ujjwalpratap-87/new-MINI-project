from __future__ import annotations

from dataclasses import dataclass

AQI_BANDS = [
    (0, 50, 'Good', '#2ecc71', 'Air quality is healthy. Maintain normal outdoor activity.'),
    (51, 100, 'Moderate', '#f1c40f', 'Sensitive people should reduce prolonged outdoor exertion.'),
    (101, 150, 'Poor', '#e67e22', 'Limit prolonged outdoor exertion and monitor symptoms.'),
    (151, 200, 'Very Poor', '#e74c3c', 'Avoid outdoor activity where possible and use a purifier indoors.'),
    (201, 500, 'Hazardous', '#8e44ad', 'Stay indoors, keep windows closed, and follow emergency guidance.'),
]


@dataclass(frozen=True)
class AQIClassification:
    label: str
    color: str
    recommendation: str


def classify_aqi(aqi_value: float) -> AQIClassification:
    value = max(0.0, min(float(aqi_value), 500.0))
    for minimum, maximum, label, color, recommendation in AQI_BANDS:
        if minimum <= value <= maximum:
            return AQIClassification(label=label, color=color, recommendation=recommendation)
    return AQIClassification(label='Hazardous', color='#8e44ad', recommendation='Stay indoors and follow local advisories.')


def get_aqi_color(aqi_value: float) -> str:
    return classify_aqi(aqi_value).color


def get_aqi_recommendation(aqi_value: float) -> str:
    return classify_aqi(aqi_value).recommendation


def get_health_indicator(aqi_value: float) -> str:
    label = classify_aqi(aqi_value).label
    return {
        'Good': 'Low risk',
        'Moderate': 'Acceptable with caution',
        'Poor': 'Elevated health risk',
        'Very Poor': 'High health risk',
        'Hazardous': 'Emergency conditions',
    }[label]
