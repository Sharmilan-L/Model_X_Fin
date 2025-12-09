# src/events/normalize.py

import json
from pathlib import Path
from typing import List

from .schema import Event, make_event_id, now_utc_iso
from src.utils.region import NATIONAL, detect_districts

DATA_RAW_DIR = Path("data/raw")
DATA_PROCESSED_DIR = Path("data/processed")


def load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 1. GOVERNMENT NEWS NORMALIZER
# ============================================================

def normalize_gov_news() -> List[Event]:
    path = DATA_RAW_DIR / "government_news.json"
    data = load_json(path) or []

    events = []

    for item in data:

        # Extract summary or fallback
        summary = (
            item.get("summary")
            or item.get("description")
            or item.get("content")
            or ""
        )

        # Fallback summary if empty
        if not summary.strip():
            summary = f"Government event reported: {item.get('title', '')}"

        # Detect districts using NLP (optional)
        districts = detect_districts(item.get("title", "") + " " + summary) or [NATIONAL]

        ev = Event(
            id=make_event_id(),
            source_type="gov",
            raw_source=item.get("source", "Government"),
            title=item.get("title", "").strip(),
            summary=summary.strip(),
            url=item.get("url"),
            timestamp=item.get("published") or item.get("fetched_at") or now_utc_iso(),
            event_type=None,
            severity=None,
            districts=districts,
            tags=["government", "official"],
            extra={"source": item.get("source", "gov")}
        )
        events.append(ev)

    return events


# ============================================================
# 2. MEDIA NEWS (RSS, Google News, YouTube, GDELT)
# ============================================================

def normalize_media_news() -> List[Event]:
    path = DATA_RAW_DIR / "sri_lanka_news.json"
    data = load_json(path) or []

    events = []

    for item in data:

        # Extract summary or fallback
        summary = (
            item.get("summary")
            or item.get("description")
            or item.get("content")
            or ""
        )

        # Prevent empty summary
        if not summary.strip():
            summary = f"News event: {item.get('title', '')}"

        districts = detect_districts(item.get("title", "") + " " + summary) or [NATIONAL]

        ev = Event(
            id=make_event_id(),
            source_type=item.get("source", "news"),
            raw_source=item.get("source", "news"),
            title=item.get("title", "").strip(),
            summary=summary.strip(),
            url=item.get("link"),
            timestamp=item.get("published") or now_utc_iso(),
            event_type=None,
            severity=None,
            districts=districts,
            tags=["news"],
            extra={"summary_length": len(summary)}
        )
        events.append(ev)

    return events


# ============================================================
# 3. WEATHER EVENTS (NEW + OLD FORMAT SUPPORTED)
# ============================================================

def normalize_weather() -> List[Event]:
    path = DATA_RAW_DIR / "srilanka_weather.json"
    data = load_json(path) or []

    events = []

    # NEW FORMAT (LIST OF RECORDS)
    if isinstance(data, list):
        for item in data:

            district = item.get("district", "Unknown")
            warnings = item.get("warnings", [])

            # Build summary from values
            summary = (
                f"Temp: {item.get('temperature')}°C, "
                f"Wind: {item.get('wind_speed')} km/h, "
                f"Rain1h: {item.get('rain_1h')} mm, "
                f"Rain3h: {item.get('rain_3h')} mm, "
                f"Humidity: {item.get('humidity')}%, "
                f"Warnings: {', '.join(warnings) if warnings else 'None'}"
            )

            # Base event
            events.append(Event(
                id=make_event_id(),
                source_type="weather",
                raw_source="OpenWeather",
                title=f"Weather update for {district}",
                summary=summary,
                url=None,
                timestamp=now_utc_iso(),
                event_type=None,
                severity=None,
                districts=[district],
                tags=["weather"],
                extra=item
            ))

            # Weather alert types
            if item.get("rain_3h", 0) >= 20:
                events.append(Event(
                    id=make_event_id(),
                    source_type="weather",
                    raw_source="OpenWeather",
                    title=f"Heavy rain alert in {district}",
                    summary=summary,
                    url=None,
                    timestamp=now_utc_iso(),
                    event_type="Heavy Rain",
                    severity=None,
                    districts=[district],
                    tags=["weather", "rain"],
                    extra=item
                ))

            if item.get("wind_speed", 0) >= 40:
                events.append(Event(
                    id=make_event_id(),
                    source_type="weather",
                    raw_source="OpenWeather",
                    title=f"Strong wind alert in {district}",
                    summary=summary,
                    url=None,
                    timestamp=now_utc_iso(),
                    event_type="Strong Wind",
                    severity=None,
                    districts=[district],
                    tags=["weather", "wind"],
                    extra=item
                ))

        return events

    # OLD FORMAT (DICT OF DISTRICTS)
    if isinstance(data, dict):
        for district, info in data.items():
            warnings = info.get("warnings", [])
            summary = info.get("weather_description", "")

            if not summary.strip():
                summary = f"Weather conditions: {warnings}"

            events.append(Event(
                id=make_event_id(),
                source_type="weather",
                raw_source="OpenWeather",
                title=f"Weather update for {district}",
                summary=summary,
                url=None,
                timestamp=now_utc_iso(),
                event_type=None,
                severity=None,
                districts=[district],
                tags=warnings,
                extra=info
            ))

        return events

    return []


# ============================================================
# MAIN BUILDER
# ============================================================

def main():
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    all_events: List[Event] = []
    all_events += normalize_gov_news()
    all_events += normalize_media_news()
    all_events += normalize_weather()

    out_path = DATA_PROCESSED_DIR / "events.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in all_events], f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_events)} normalized events → {out_path}")


if __name__ == "__main__":
    main()
