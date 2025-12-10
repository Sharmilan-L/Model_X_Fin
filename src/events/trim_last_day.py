import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

EVENTS_PATH = Path("data/processed/events.json")

def trim_last_day():
    if not EVENTS_PATH.exists():
        print("events.json not found.")
        return

    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        events = json.load(f)

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=2)

    kept = []
    for ev in events:
        ts = ev.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "")).replace(tzinfo=timezone.utc)
            if dt >= cutoff:
                kept.append(ev)
        except:
            kept.append(ev)

    with open(EVENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(kept, f, indent=2, ensure_ascii=False)

    print(f"[trim] Kept {len(kept)} events (last 24h)")
