# run_pipeline.py

import subprocess

COMMANDS = [
    "python -m src.scrapers.news_collector",
    "python -m src.scrapers.gov_collector",
    "python -m src.scrapers.weather_collector",
    "",
    "python -m src.events.normalize",
    "python -m src.events.trim_last_day",   # If you want last 24 hours only
    "python -m src.events.classify_advanced",
    "python -m src.events.severity",
    "",
    "python -m src.industry.score",
    "python -m src.industry.score_district",
    "python -m src.district.aggregate"


]

def run(cmd):
    if not cmd.strip():
        print("\n-------------------------\n")
        return
    print(f"\n\n=== RUNNING: {cmd} ===")
    subprocess.call(cmd, shell=True)

def main():
    print("\n====================================")
    print("     SRI LANKA REALTIME PIPELINE")
    print("====================================\n")

    for cmd in COMMANDS:
        run(cmd)

    print("\n====================================")
    print("     PIPELINE COMPLETE ✔")
    print("====================================\n")

if __name__ == "__main__":
    main()
