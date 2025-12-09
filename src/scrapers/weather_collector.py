import requests
import json
import time
from src.scrapers import weather_key

from pathlib import Path   

def save_with_limited_history(path, new_items, max_items=8000):
    import json

    # Load existing (must be a list, otherwise reset)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []  # FIX: convert invalid dict → list
        except:
            existing = []
    else:
        existing = []

    # Combine
    combined = existing + new_items

    # Weather has no URL → use district + timestamp to dedupe
    seen = set()
    unique = []
    for it in combined:
        uid = (it.get("district"), it.get("timestamp"))
        if uid not in seen:
            seen.add(uid)
            unique.append(it)

    # Keep only the last max_items
    unique = unique[-max_items:]

    # Save back
    with open(path, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

    print(f"[+] Stored {len(unique)} items → {path}")



# ================================
#  CONFIGURATION
# ================================
API_KEY = weather_key.OPENWEATHER

# Sri Lanka district coordinates (central reference points)
DISTRICTS = {
    "Colombo": (6.9271, 79.8612),
    "Gampaha": (7.0897, 79.9921),
    "Kalutara": (6.5770, 79.9629),
    "Kandy": (7.2906, 80.6337),
    "Matale": (7.4675, 80.6234),
    "Nuwara Eliya": (6.9497, 80.7891),
    "Galle": (6.0535, 80.2210),
    "Matara": (5.9549, 80.5540),
    "Hambantota": (6.1240, 81.1185),
    "Jaffna": (9.6615, 80.0255),
    "Kilinochchi": (9.3961, 80.3980),
    "Mannar": (8.9809, 79.9047),
    "Vavuniya": (8.7542, 80.4973),
    "Mullaitivu": (9.2671, 80.8140),
    "Batticaloa": (7.7300, 81.6924),
    "Trincomalee": (8.5874, 81.2152),
    "Ampara": (7.2910, 81.6724),
    "Badulla": (6.9896, 81.0560),
    "Monaragala": (6.8720, 81.3500),
    "Kurunegala": (7.4863, 80.3647),
    "Puttalam": (8.0408, 79.8393),
    "Anuradhapura": (8.3114, 80.4037),
    "Polonnaruwa": (7.9396, 81.0036),
    "Ratnapura": (6.7056, 80.3847),
    "Kegalle": (7.2513, 80.3464)
}

# ================================
#  WEATHER FETCH FUNCTION
# ================================
def fetch_weather(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("message", "unknown error")}

        # Extract useful fields only
        weather_info = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "wind_gust": data["wind"].get("gust", None),
            "rain_1h": data.get("rain", {}).get("1h", 0),
            "rain_3h": data.get("rain", {}).get("3h", 0),
            "weather_main": data["weather"][0]["main"],
            "weather_description": data["weather"][0]["description"],
            "clouds": data["clouds"]["all"],
            "visibility": data.get("visibility", None)
        }

        # Detect potential warnings
        warnings = []
        if weather_info["wind_speed"] > 10:
            warnings.append("High Wind")
        if weather_info["rain_1h"] > 5:
            warnings.append("Heavy Rainfall")
        if weather_info["weather_main"] in ["Thunderstorm"]:
            warnings.append("Thunderstorm Risk")

        weather_info["warnings"] = warnings

        return weather_info

    except Exception as e:
        return {"error": str(e)}

# ================================
#  MAIN EXECUTION
# ================================
def main():
    final_output = {}

    print("Fetching Sri Lanka district weather data...\n")

    for district, (lat, lon) in DISTRICTS.items():
        print(f"Processing: {district}")
        weather = fetch_weather(lat, lon)
        final_output[district] = weather
        time.sleep(1.2)  # to avoid free API rate limits

    # Save JSON file
    save_with_limited_history(
            Path("data/raw/srilanka_weather.json"),
            [ {"district": d, **w} for d, w in final_output.items() ]
        )


    print("\nCompleted! Weather data saved as: srilanka_weather.json")


if __name__ == "__main__":
    main()
