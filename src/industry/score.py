# src/industry/score.py

import json
from pathlib import Path
from src.industry.sensitivity import SENSITIVITY_MATRIX, INDUSTRIES
from .footprint import INDUSTRY_REGIONS, district_to_province

EVENTS_PATH = Path("data/processed/events.json")
OUTPUT_PATH = Path("data/processed/industry_scores.json")

HIGH = 0.6
MEDIUM = 0.3

# ----------------------------------------------------
# LOCATION FACTOR FUNCTION
# ----------------------------------------------------
def location_factor(industry: str, event_districts: list):
    """
    Returns how strongly an event's location affects the industry.
    """
    if not event_districts or event_districts == ["NATIONAL"]:
        return 0.6  # national-level relevance

    industry_provinces = INDUSTRY_REGIONS.get(industry, [])
    
    max_factor = 0.1  # default low influence

    for district in event_districts:
        province = district_to_province(district)

        if not province:
            continue

        if province in industry_provinces:
            # district belongs to an industry-active province
            max_factor = max(max_factor, 1.0)
        else:
            # same country but not core region
            max_factor = max(max_factor, 0.3)

    return max_factor


# ----------------------------------------------------
# INDUSTRY SCORING ENGINE
# ----------------------------------------------------
def score_industries():
    if not EVENTS_PATH.exists():
        print("events.json not found!")
        return

    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        events = json.load(f)

    results = {}

    for industry in INDUSTRIES:
        risk_raw = 0
        opp_raw = 0
        drivers = []

        for ev in events:
            etype = ev.get("event_type")
            sev = ev.get("severity", 0)
            districts = ev.get("districts", ["NATIONAL"])

            if etype not in SENSITIVITY_MATRIX:
                continue

            sens = SENSITIVITY_MATRIX[etype][industry]

            loc_factor = location_factor(industry, districts)

            impact = (sev * sens * loc_factor) / 2
            # Industry exposure correction (Fix #5)
            if industry == "IT":
                impact *= 0.25      # IT is minimally affected by weather/disasters

            if industry == "Banking":
                impact *= 0.5      # Banking moderately affected by economic/political events

            if industry == "Energy":
                impact *= 0.7      # Energy affected by storms, outages, but not extreme

            if industry == "Tourism":
                impact *= 0.8      # Tourism is sensitive, but not as severely as Apparel/Logistics

            if industry == "Agriculture":
                impact *= 1.2      # Agriculture is HIGHLY sensitive to weather conditions

            if industry == "Water":
                impact *= 1.2      # Water industry benefits strongly from weather events

            if industry == "Logistics":
                impact *= 1.0      # Logistics heavily affected by roads/weather

            if industry == "Apparel":
                impact *= 1.0      # Apparel very dependent on transport and weather

            if industry == "Retail":
                impact *= 0.9      # Some sensitivity but less extreme


            drivers.append((impact, ev.get("title", "")))

            if impact > 0:
                opp_raw += impact
            else:
                risk_raw += abs(impact)

        # normalize
        risk = min(risk_raw, 0.8)
        opp = min(opp_raw, 0.85)

        risk_level = (
            "High" if risk >= HIGH else
            "Medium" if risk >= MEDIUM else
            "Low"
        )

        opp_level = (
            "High" if opp >= HIGH else
            "Medium" if opp >= MEDIUM else
            "Low"
        )

        drivers = sorted(drivers, key=lambda x: abs(x[0]), reverse=True)[:3]

        results[industry] = {
            "risk_score": round(risk, 2),
            "opp_score": round(opp, 2),
            "risk_level": risk_level,
            "opp_level": opp_level,
            "top_drivers": [d[1] for d in drivers]
        }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Regional industry scoring complete →", OUTPUT_PATH)


if __name__ == "__main__":
    score_industries()
