import json
from pathlib import Path

FILE = Path("data/processed/district_scores.json")

def level(score):
    if score >= 0.6:
        return "High"
    elif score >= 0.3:
        return "Medium"
    else:
        return "Low"

def main():
    with open(FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for district, industries in data.items():

        risk_values = []
        opp_values = []

        # Collect only industries (not district-level keys)
        for name, ind in industries.items():
            if isinstance(ind, dict) and "risk_score" in ind:
                risk_values.append(ind.get("risk_score", 0))
                opp_values.append(ind.get("opp_score", 0))

        # Avoid division by zero
        if len(risk_values) == 0:
            avg_risk = 0
            avg_opp = 0
        else:
            avg_risk = round(sum(risk_values) / len(risk_values), 2)
            avg_opp = round(sum(opp_values) / len(opp_values), 2)

        # Add district-level metrics
        data[district]["risk_score"] = avg_risk
        data[district]["opp_score"] = avg_opp
        data[district]["risk_level"] = level(avg_risk)
        data[district]["opp_level"] = level(avg_opp)
        data[district]["event_count"] = len(risk_values)

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("District-level aggregation complete ✔")

if __name__ == "__main__":
    main()
