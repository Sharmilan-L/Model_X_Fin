# src/events/classify.py

import json
from pathlib import Path

EVENTS_PATH = Path("data/processed/events.json")


# -----------------------------
# 1. Category Keyword Dictionary
# -----------------------------
CLASSIFICATION_RULES = {
    # WEATHER & DISASTERS
    "Flood": [
        "flood", "flooding", "water level", "river overflow",
        "inundation", "flash flood", "flood warning", "dam overflow",
        "high water level", "overflowing", "river burst"
    ],
    "Heavy Rain": [
        "heavy rain", "heavy rainfall", "showers", "monsoon",
        "downpour", "torrential rain", "rain warning", "adverse weather"
    ],
    "Landslide": [
        "landslide", "lands slip", "slope failure", "nbro warning",
        "hill collapse", "unstable slope"
    ],
    "Drought": [
        "drought", "dry spell", "water shortage", "heatwave",
        "extreme heat", "irrigation issue"
    ],
    "Strong Wind": [
        "strong wind", "gale", "wind advisory", "cyclonic wind",
        "high wind", "monsoon wind"
    ],
    "Cyclone": [
        "cyclone", "tropical storm", "depression", "low pressure area",
        "storm surge", "cyclonic system"
    ],
    "Lightning": [
        "lightning", "thunderstorm", "thundershowers", "lightning advisory"
    ],

    # TRANSPORTATION & LOGISTICS
    "Transport Disruption": [
        "traffic", "road closed", "accident", "collision",
        "road blockage", "highway closed", "road diversion"
    ],
    "Train Issue": [
        "train delay", "train cancelled", "railway strike",
        "train derailment", "slr strike", "train accident"
    ],
    "Bus Issue": [
        "bus strike", "bus service", "sltb strike", "private bus strike"
    ],
    "Port Disruption": [
        "port delay", "port congestion", "container backlog",
        "colombo port", "sagt delay"
    ],

    # ECONOMIC & POLICY
    "Fuel Price Increase": [
        "fuel price", "petrol price", "diesel price", "cpc price",
        "lp gas price", "kerosene price"
    ],
    "Policy Change": [
        "cabinet", "policy", "vat", "tax", "regulation", "government approved",
        "import ban", "tariff", "decision"
    ],
    "Economic Update": [
        "cbsl", "inflation", "interest rate", "gdp", "forex",
        "rupee", "depreciation", "economic crisis"
    ],

    # SOCIAL EVENTS
    "Strike": [
        "strike", "hartal", "protest", "union action", "walkout",
        "demonstration"
    ],
    "Crime Event": [
        "shooting", "robbery", "attack", "assault", "kidnap"
    ],
    "Political Event": [
        "parliament", "cabinet", "president", "pm", "political rally",
        "election"
    ],

    # HEALTH
    "Health Alert": [
        "dengue", "dengue outbreak", "covid", "virus", "epidemic",
        "hospital overload", "health advisory"
    ],

    # TOURISM
    "Tourism": [
        "tourist", "travel advisory", "visa-free", "arrival",
        "hotel booking", "sri lankan airlines"
    ],

    # INDUSTRY / OPERATIONS
    "Factory Incident": [
        "factory fire", "factory shutdown", "warehouse fire",
        "production halt", "machine failure"
    ],
}


def classify_text(text: str) -> str:
    """Return the event type based on keyword matching."""
    text = text.lower()

    for category, keywords in CLASSIFICATION_RULES.items():
        for kw in keywords:
            if kw in text:
                return category

    return "General"   # fallback category


# -----------------------------
# 2. Main Classifier Function
# -----------------------------
def classify_events():
    if not EVENTS_PATH.exists():
        print("events.json not found!")
        return

    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        events = json.load(f)

    for ev in events:
        title = ev.get("title", "").lower()
        summary = ev.get("summary", "").lower()

        combined_text = title + " " + summary
        ev_type = classify_text(combined_text)

        ev["event_type"] = ev_type

    # save back
    with open(EVENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"Classification complete. Updated {len(events)} events.")


if __name__ == "__main__":
    classify_events()
