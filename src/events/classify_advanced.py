# src/events/classify_advanced.py

import json
from pathlib import Path
from nltk.stem import PorterStemmer
from fuzzywuzzy import fuzz
from src.utils.region import DISTRICTS, NATIONAL

EVENTS_PATH = Path("data/processed/events.json")

ps = PorterStemmer()

# --------------------------------------------------------------------
# 1. BIG keyword library (English + Sinhala + Tamil, optimized size)
# --------------------------------------------------------------------
ADVANCED_RULES = {
    # --- WEATHER & DISASTERS ------------------------------------------------
    "Flood": [
        # English
        "flood", "flooding", "flash flood", "flood water", "flooded",
        "inundation", "inundated", "water level rising", "river overflow",
        "river burst", "bank overflow", "reservoir spill", "dam overflow",
        "low lying areas under water", "roads under water",
        # Sinhala
        "ගංවතුර", "ජල මට්ටම", "ජල මට්ටම ඉහළ", "වැලි පල්ලටුව",
        "වේලි ඇරිය", "නදී ජලය පිරී", "පස බිම ගිලෙනවා",
        # Tamil
        "வெள்ளம்", "வெள்ளப்பெருக்கு", "நீர்மட்டம் உயர்வு",
        "ஆறு கரை மீறி", "நீர் மூழ்கியது"
    ],

    "Heavy Rain": [
        # English
        "heavy rain", "torrential rain", "rainfall", "showers",
        "thundershowers", "rain storm", "monsoon rain",
        "adverse weather", "bad weather", "rain warning",
        "downpour", "cloudburst",
        # Sinhala
        "වැසි", "අධික වැසි", "මහ වැසි", "වැසි තත්ත්වය",
        "කුණාටු සහිත වැසි", "අවදානම් කාලගුණ",
        # Tamil
        "மழை", "கனமழை", "முழு மழை", "மழை எச்சரிக்கை",
        "இடியுடன் கூடிய மழை"
    ],

    "Landslide": [
        "landslide", "land slip", "earth slip", "slope failure",
        "mudslide", "hill collapse", "unstable slope", "nbro warning",
        # Sinhala
        "පස් කන්ද", "බිම අත්පත් වීම", "බිම ගිලී", "භූස්කරය",
        # Tamil
        "நிலச்சரிவு", "பூமிச்சரிவு", "மண் சரிவு"
    ],

    "Drought": [
        "drought", "dry spell", "water shortage", "no rainfall",
        "irrigation failure", "crop drying", "heatwave", "extreme heat",
        # Sinhala
        "දහඩිය", "දිය නොමැති", "ජල හිඟය", "උණ පීඩා",
        # Tamil
        "வறட்சி", "தண்ணீர் தட்டுப்பாடு", "வெப்ப அலை"
    ],

    "Strong Wind": [
        "strong wind", "gale force wind", "high winds", "monsoon wind",
        "gusty wind", "wind advisory", "wind warning",
        # Sinhala
        "සුළං", "තද සුළං", "සුළං දරුණු", "සුළං හමා",
        # Tamil
        "கனத்த காற்று", "வேகமான காற்று", "புயல் காற்று"
    ],

    "Cyclone": [
        "cyclone", "tropical storm", "low pressure area",
        "storm surge", "cyclonic system", "deep depression",
        # Sinhala
        "කුණාටුව", "අවපීඩන බලකේන්ද්‍රය",
        # Tamil
        "புயல்", "குறைந்த காற்றழுத்த பகுதி"
    ],

    "Lightning": [
        "lightning", "lightning strikes", "thunderstorm",
        "electrical storm", "lightning advisory",
        # Sinhala
        "මෙරුණු", "අකුණ", "අකුණු පහර",
        # Tamil
        "மின்னல்", "இடி மின்னல்"
    ],

    # --- TRANSPORT & LOGISTICS ---------------------------------------------
    "Train Issue": [
        "train delay", "train cancelled", "train cancellation",
        "railway strike", "rail strike", "train strike",
        "train derailment", "train accident", "locomotive failure",
        "slr strike", "railway line blocked"
    ],

    "Bus Issue": [
        "bus strike", "sltb strike", "private bus strike",
        "bus service suspended", "bus service disrupted",
        "no bus service", "bus protest"
    ],

    "Transport Disruption": [
        "traffic jam", "heavy traffic", "road closed", "road closure",
        "road blocked", "highway closed", "bridge collapsed",
        "road diversion", "vehicle breakdown", "multi vehicle collision",
        "road accident", "fatal accident", "road flooded", "traffic congestion"
    ],

    "Port Disruption": [
        "port congestion", "shipping delay", "container backlog",
        "colombo port", "sagt delay", "port strike",
        "harbour closed", "terminal shutdown", "vessel delay"
    ],

    "Airport Issue": [
        "flight delay", "flight cancelled", "schedule disruption",
        "airport congestion", "runway closed", "air traffic control issue"
    ],

    # --- ECONOMY & POLICY ---------------------------------------------------
    "Fuel Price Increase": [
        # English
        "fuel price", "petrol price", "diesel price", "fuel hike",
        "fuel revision", "cpc price", "pump price increase",
        "lp gas price", "gas price increase", "kerosene price",
        "fuel surcharge",
        # Sinhala
        "ඉන්ධන මිල", "පෙට්‍රල් මිල", "ඩීසල් මිල", "ඉන්ධන ඉහළ දැමීම",
        "අමතර ඉන්ධන ගාස්තු",
        # Tamil
        "எரிபொருள் விலை", "பெட்ரோல் விலை", "டீசல் விலை",
        "விலை உயர்வு", "எரிவாயு விலை"
    ],

    "Policy Change": [
        "vat increase", "tax revision", "tax hike", "new tax",
        "government policy", "cabinet decision", "regulation change",
        "import ban", "import restriction", "tariff change",
        "license requirement", "price control", "subsidy removed",
        # Sinhala
        "ණය ප්‍රතිපත්තිය", "බදු සංශෝධනය", "පාලනාත්මක මිල",
        "ආනයන තහනම් කිරීම",
        # Tamil
        "வரி உயர்வு", "ஆட்சியின் தீர்மானம்"
    ],

    "Economic Update": [
        "cbsl", "central bank", "policy rate", "interest rate",
        "inflation", "gdp growth", "economic growth", "economic slowdown",
        "recession", "rupee depreciation", "exchange rate",
        "foreign reserves", "unemployment", "debt restructuring",
         # Sinhala
        "මූල්‍ය ප්‍රතිපත්තිය", "අර්ථිකය", "මුදල් අමිලය",
        # Tamil
        "பொருளாதார", "ரூபாய் மதிப்பு குறைவு"
    ],

     "Currency Fluctuation": [
        "rupee", "exchange rate", "forex", "currency depreciation",
        # Sinhala
        "විනිමය අනුපාතය", "රුපියල අඩුවීම",
        # Tamil
        "ரூபாய் வீழ்ச்சி"
    ],

    # --- SOCIAL / LABOUR ----------------------------------------------------
    "Strike": [
        "strike", "hartal", "union action", "work stoppage",
        "work to rule", "industrial action", "walkout", "labour protest",
        "trade union protest"
    ],

    "Crime Event": [
        "shooting", "murder", "homicide", "knife attack",
        "armed robbery", "robbery", "burglary", "kidnap",
        "drug bust", "narcotics seizure", "explosion", "bomb blast",
        "fire outbreak", "arson",
        # Sinhala
        "වර්ජනය", "හර්තාලය", "මේස වර්ජනය",
        # Tamil
        "வேலைநிறுத்தம்"
    ],
    "Protest": [
        "protest", "demonstration", "march", "riot",
        # Sinhala
        "ප්රదర్శනය", "එරෙහි පුරප්පාට", "සඹර",  
        # Tamil
        "ஆர்ப்பாட்டம்"
    ],
    
    "Crime Event": [
        "shooting", "murder", "robbery", "explosion", "bomb blast",
        # Sinhala
        "කොල්ලකෑම", "ඝාතනය", "ප්‍රහාරය",
        # Tamil
        "குற்றம்", "தாக்குதல்"
    ],

    "Political Event": [
        "president", "prime minister", "parliament", "cabinet meeting",
        "political rally", "election", "polling", "dissolution of parliament",
        "no confidence motion", "political crisis",
        # Sinhala
        "නායක", "විපක්ෂය", "මැතිවරණය",
        # Tamil
        "தேர்தல்", "அரசு"
    ],

    # --- HEALTH -------------------------------------------------------------
    "Health Alert": [
        "dengue outbreak", "dengue cases", "dengue rise",
        "viral fever", "virus outbreak", "health warning",
        "epidemic", "disease spread", "hospital overload",
        "covid", "coronavirus", "influenza",
        # Sinhala
        "ඩෙංගු", "වයිරස්", "සෞඛ්‍ය අනතුරු අඟවිකර",
        # Tamil
        "டெங்குச்சூடு", "வைரஸ்", "சுகாதார எச்சரிக்கை"
    ],

    # --- TOURISM ------------------------------------------------------------
    "Tourism": [
        "tourist arrivals", "tourist arrival", "hotel bookings",
        "holiday season", "tourism boom", "travel advisory",
        "visa free", "visa on arrival", "charter flights",
        "tourism promotion", "occupancy rate",
        # Sinhala
        "ප්රවේශන වීසා", "සෞඛ්‍ය උපදෙස්",
        # Tamil
        "சுற்றுலா"
    ],

    # --- INDUSTRIAL / UTILITIES --------------------------------------------
    "Factory Incident": [
        "factory fire", "warehouse fire", "industrial accident",
        "production halt", "production stopped", "plant shutdown",
        "factory closure", "machine breakdown", "equipment failure",
        # Sinhala
        "කර්මාන්ත ශාලාව", "වැසීම", "ගින්න",
        # Tamil
        "தொழிற்சாலை தீ", "தொழிற் விபத்து"
    ],

    "Power Cut": [
        "power cut", "electricity outage", "blackout",
        "load shedding", "power failure", "grid failure",
        # Sinhala
        "විදුලිය කප්පාදුව", "බල මඟ හරවී",
        # Tamil
        "மின்தடை", "மின்தடைப்பு"
    ],

    "Water Supply Issue": [
        "water cut", "no water supply", "pipe burst",
        "water disruption", "water supply interruption",
        # Sinhala
        "ජල කප්පාදුව", "ජල හිඟය", "ජල බිඳවැටීම",
        # Tamil
        "தண்ணீர் தடை", "தண்ணீர் தட்டுப்பாடு"
        
    ]
}

# --------------------------------------------------------------------
# 2. NLP-style matching + fuzzy phrase matching
# --------------------------------------------------------------------
def nlp_match(text: str, keywords) -> bool:
    """
    Advanced match:
    - lowercased contains
    - fuzzy phrase match
    """
    text = text.lower()

    for kw in keywords:
        kw = kw.lower()

        # direct substring
        if kw in text:
            return True

        # fuzzy phrase similarity
        if len(kw.split()) > 1 and fuzz.partial_ratio(kw, text) >= 80:
            return True

    return False


# --------------------------------------------------------------------
# 3. Headline clustering for trends
# --------------------------------------------------------------------
def cluster_headlines(headlines):
    clusters = []
    used = set()

    for i, h1 in enumerate(headlines):
        if i in used:
            continue
        cluster = [h1]
        used.add(i)
        for j, h2 in enumerate(headlines):
            if j in used:
                continue
            if fuzz.token_set_ratio(h1, h2) >= 75:
                cluster.append(h2)
                used.add(j)
        clusters.append(cluster)
    return clusters


def source_confidence(source_type: str) -> float:
    """
    Multi-source / reliability boost.
    gov > weather > major news > other.
    """
    source_type = (source_type or "").lower()
    if source_type == "gov":
        return 0.4
    if source_type == "weather":
        return 0.3
    if source_type in ("rss", "google_news", "news"):
        return 0.2
    if source_type in ("youtube", "gdelt"):
        return 0.1
    return 0.0


# --------------------------------------------------------------------
# 4. Main advanced classifier
# --------------------------------------------------------------------
def classify_events_advanced():
    if not EVENTS_PATH.exists():
        print("events.json not found!")
        return

    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        events = json.load(f)

    # Build clusters of similar headlines
    titles = [ev.get("title", "") for ev in events]
    clusters = cluster_headlines(titles)
    cluster_sizes = {t: len(c) for c in clusters for t in c}

    for ev in events:
        title = ev.get("title", "") or ""
        summary = ev.get("summary", "") or ""
        text = f"{title} {summary}".strip()

        # pick best matching category
        chosen_type = "General"
        for category, keywords in ADVANCED_RULES.items():
            if nlp_match(text, keywords):
                chosen_type = category
                break

        ev["event_type"] = chosen_type

        # trend strength = how many similar headlines we saw
        tsize = cluster_sizes.get(title, 1)
        ev["trend_strength"] = tsize

        # confidence = base 0.5 + trend + source reliability
        base = 0.5
        conf = base + 0.05 * min(tsize - 1, 5) + source_confidence(ev.get("source_type"))
        ev["confidence"] = round(min(conf, 1.0), 2)

    with open(EVENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"Advanced classification complete for {len(events)} events.")


if __name__ == "__main__":
    classify_events_advanced()
