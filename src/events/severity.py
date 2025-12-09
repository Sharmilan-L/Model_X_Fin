# src/events/severity.py

import json
from pathlib import Path
from datetime import datetime, timedelta,timezone

EVENTS_PATH = Path("data/processed/events.json")

# ------------------------------
# Source reliability weights
# ------------------------------
SOURCE_WEIGHTS = {
    "gov": 1.0,
    "weather": 0.9,
    "rss": 0.8,
    "google_news": 0.75,
    "news": 0.7,
    "youtube": 0.5,
    "gdelt": 0.6,
    "general": 0.5
}

# ------------------------------
# Event type severity base weight
# ------------------------------
EVENT_TYPE_WEIGHTS = {
    "Flood": 1.0,
    "Landslide": 1.0,
    "Cyclone": 1.0,

    "Heavy Rain": 0.8,
    "Strong Wind": 0.7,
    "Lightning": 0.6,
    "Drought": 0.6,

    "Fuel Price Increase": 0.8,
    "Strike": 0.75,
    "Transport Disruption": 0.6,
    "Train Issue": 0.6,
    "Bus Issue": 0.6,
    "Port Disruption": 0.6,
    "Airport Issue": 0.6,

    "Policy Change": 0.5,
    "Economic Update": 0.5,

    "Health Alert": 0.85,
    "Tourism": 0.3,
    "Crime Event": 0.4,
    "Political Event": 0.3,
    "Factory Incident": 0.65,
    "Power Cut": 0.6,
    "Water Supply Issue": 0.6,

    "General": 0.2
}


# ------------------------------
# Recency decay (events lose strength over time)
# ------------------------------
from datetime import datetime, timedelta, timezone

def recency_weight(timestamp_str):
    if not timestamp_str:
        return 1.0

    try:
        # Convert Z → +00:00 for ISO parsing
        clean = timestamp_str.replace("Z", "+00:00")

        ts = datetime.fromisoformat(clean)

        # If timestamp is naive, make it UTC
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        # Current time as timezone-aware UTC
        now = datetime.now(timezone.utc)

        hours_old = (now - ts).total_seconds() / 3600

    except Exception as e:
        # fallback if parsing fails
        return 1.0

    if hours_old < 1:
        return 1.0
    if hours_old < 6:
        return 0.8
    if hours_old < 24:
        return 0.6
    if hours_old < 72:
        return 0.3
    return 0.1



# ------------------------------
# Weather intensity scoring
# ------------------------------
def compute_weather_intensity(event):
    extra = event.get("extra", {})
    rain = extra.get("rain_1h") or extra.get("rain_3h") or 0
    wind = extra.get("wind_speed", 0)

    rain_intensity = min(rain / 30, 1.0)  # 30mm/h = max
    wind_intensity = min(wind / 70, 1.0)  # 70 km/h = storm

    return max(rain_intensity, wind_intensity)


# ------------------------------
# Final severity calculation
# ------------------------------
def compute_severity(event):
    source = event.get("source_type", "general")
    etype = event.get("event_type", "General")

    source_w = SOURCE_WEIGHTS.get(source, 0.5)
    type_w = EVENT_TYPE_WEIGHTS.get(etype, 0.2)

    # trend strength from headline clustering
    trend_strength = event.get("trend_strength", 1)
    trend_score = min((trend_strength - 1) / 15, 0.4) # 6+ headlines = max

    confidence = event.get("confidence", 0.5)

    weather_intensity = compute_weather_intensity(event)

    recency = recency_weight(event.get("timestamp"))

    severity = (
        0.30 * source_w +
        0.25 * type_w +
        0.15 * trend_score +
        0.15 * confidence +
        0.10 * weather_intensity +
        0.05 * recency
    )

    severity = min(severity, 0.85)  # soft cap
    return round(severity, 2)



# ------------------------------
# Apply severity to all events
# ------------------------------
def apply_severity():
    if not EVENTS_PATH.exists():
        print("events.json not found!")
        return

    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        events = json.load(f)

    for ev in events:
        ev["severity"] = compute_severity(ev)

    with open(EVENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"Upgraded severity scoring complete for {len(events)} events.")


if __name__ == "__main__":
    apply_severity()
