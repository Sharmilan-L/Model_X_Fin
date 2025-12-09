# src/industry/score_district.py

import json
from pathlib import Path
from src.industry.sensitivity import SENSITIVITY_MATRIX, INDUSTRIES
from src.industry.footprint import INDUSTRY_REGIONS, district_to_province

EVENTS_PATH = Path("data/processed/events.json")
OUTPUT_PATH = Path("data/processed/district_scores.json")

HIGH = 0.6
MEDIUM = 0.3

# Full Sri Lanka district list
ALL_DISTRICTS = [
    "Colombo","Gampaha","Kalutara","Kandy","Matale","Nuwara Eliya","Galle","Matara",
    "Hambantota","Jaffna","Kilinochchi","Mannar","Vavuniya","Mullaitivu",
    "Batticaloa","Trincomalee","Ampara",
    "Badulla","Monaragala","Kurunegala","Puttalam",
    "Anuradhapura","Polonnaruwa",
    "Ratnapura","Kegalle"
]


# -----------------------------------------
# Simple district-level location factor
# -----------------------------------------
def location_factor(industry, district):
    """Boosts impact if the industry is active in that district's province."""
    province = district_to_province(district)
    industry_provinces = INDUSTRY_REGIONS.get(industry, [])

    if province in industry_provinces:
        return 1.0      # core region → full effect
    return 0.4          # different region → partial effect


# -----------------------------------------
# MAIN DISTRICT SCORING ENGINE
# -----------------------------------------
def score_districts():

    if not EVENTS_PATH.exists():
        print("events.json not found!")
        return

    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        events = json.load(f)

    district_scores = {}

    # For every district in SL
    for dist in ALL_DISTRICTS:
        district_scores[dist] = {}

        # Filter only events that occurred in this district
        dist_events = [
            ev for ev in events 
            if dist in ev.get("districts", [])
        ]

        # For every industry
        for industry in INDUSTRIES:
            risk_raw = 0
            opp_raw = 0
            drivers = []

            for ev in dist_events:
                etype = ev.get("event_type")
                sev = ev.get("severity", 0)

                if etype not in SENSITIVITY_MATRIX:
                    continue

                sens = SENSITIVITY_MATRIX[etype][industry]
                loc = location_factor(industry, dist)

                # final impact score
                impact = sev * sens * loc

                drivers.append((impact, ev.get("title", "")))

                if impact > 0:
                    opp_raw += impact
                else:
                    risk_raw += abs(impact)

            # Normalize
            risk = min(risk_raw, 1.0)
            opp = min(opp_raw, 1.0)

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

            # Pick 3 strongest drivers
            top = sorted(drivers, key=lambda x: abs(x[0]), reverse=True)[:3]

            district_scores[dist][industry] = {
                "risk_score": round(risk, 2),
                "opp_score": round(opp, 2),
                "risk_level": risk_level,
                "opp_level": opp_level,
                "top_drivers": [t[1] for t in top]
            }

    # Save output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(district_scores, f, indent=2, ensure_ascii=False)

    print("District-level scoring complete →", OUTPUT_PATH)


if __name__ == "__main__":
    score_districts()
