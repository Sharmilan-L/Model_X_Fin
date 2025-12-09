# dashboard/app.py

import json
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd
import pydeck as pdk

# Optional auto-refresh (every 5 min)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=300000, key="autoRefresh")  # 300,000 ms = 5 minutes
except Exception:
    pass

# Try to import your model configs for impact calculation
try:
    from src.industry.sensitivity import SENSITIVITY_MATRIX, INDUSTRIES
    from src.industry.footprint import INDUSTRY_REGIONS, district_to_province
except Exception:
    SENSITIVITY_MATRIX = {}
    INDUSTRIES = []
    INDUSTRY_REGIONS = {}

    def district_to_province(d):
        return None

# --------------------------------------------------------------------
# DISTRICT → COORDINATES (approximate centroids for map)
# --------------------------------------------------------------------
DISTRICT_COORDS = {
    # Western
    "Colombo": (6.9271, 79.8612),
    "Gampaha": (7.0873, 79.9994),
    "Kalutara": (6.5854, 80.1010),
    # Central
    "Kandy": (7.2906, 80.6337),
    "Matale": (7.4675, 80.6234),
    "Nuwara Eliya": (6.9497, 80.7891),
    # Southern
    "Galle": (6.0535, 80.2210),
    "Matara": (5.9485, 80.5350),
    "Hambantota": (6.1246, 81.1185),
    # Northern
    "Jaffna": (9.6615, 80.0255),
    "Kilinochchi": (9.3966, 80.3982),
    "Mannar": (8.9806, 79.9046),
    "Vavuniya": (8.7500, 80.5000),
    "Mullaitivu": (9.2671, 80.8128),
    # Eastern
    "Batticaloa": (7.7170, 81.7000),
    "Trincomalee": (8.5711, 81.2335),
    "Ampara": (7.3000, 81.6667),
    # North Western
    "Kurunegala": (7.4863, 80.3647),
    "Puttalam": (8.0362, 79.8283),
    # North Central
    "Anuradhapura": (8.3114, 80.4037),
    "Polonnaruwa": (7.9396, 81.0007),
    # Uva
    "Badulla": (6.9934, 81.0550),
    "Monaragala": (6.8726, 81.3450),
    # Sabaragamuwa
    "Ratnapura": (6.7055, 80.3847),
    "Kegalle": (7.2513, 80.3464),
}

# --------------------------------------------------------------------
# STREAMLIT CONFIG & THEME
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Sri Lanka Industry Risk Intelligence",
    page_icon="🌙",
    layout="wide",
)

# Dark theme CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #161B22;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        border: 1px solid #21262D;
        box-shadow: 0 0 10px rgba(0,0,0,0.35);
    }
    .metric-title {
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: #FFFFFF;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #9DA5B4;
        margin-bottom: 0.35rem;
    }
    .badge {
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #FFF;
        margin-right: 0.35rem;
    }
    .badge-risk-high { background: #FF4C4C; }
    .badge-risk-medium { background: #FF9F1C; }
    .badge-risk-low { background: #2ECC71; }

    .badge-opp-high { background: #00C853; }
    .badge-opp-medium { background: #F1C40F; color: #111; }
    .badge-opp-low { background: #C0392B; }

    .driver-text {
        font-size: 0.8rem;
        color: #9DA5B4;
        margin-top: 0.35rem;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
        color: #FFFFFF;
    }
    .section-subtitle {
        font-size: 0.85rem;
        color: #9DA5B4;
        margin-bottom: 0.8rem;
    }
    .event-row {
        padding: 0.45rem 0;
        border-bottom: 1px solid #21262D;
    }
    .event-title {
        font-size: 0.9rem;
        font-weight: 500;
        color: #FFFFFF;
    }
    .event-meta {
        font-size: 0.78rem;
        color: #9DA5B4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------
# DATA LOADING HELPERS
# --------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_industry_scores(path: str = "data/processed/industry_scores.json"):
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_events(path: str = "data/processed/events.json"):
    p = Path(path)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_file_mtime(path: str):
    p = Path(path)
    if not p.exists():
        return None
    ts = p.stat().st_mtime
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


# --------------------------------------------------------------------
# STYLING HELPERS
# --------------------------------------------------------------------
def risk_badge(level: str) -> str:
    level = (level or "").lower()
    if level == "high":
        cls = "badge-risk-high"; label = "HIGH"
    elif level == "medium":
        cls = "badge-risk-medium"; label = "MEDIUM"
    else:
        cls = "badge-risk-low"; label = "LOW"
    return f'<span class="badge {cls}">Risk: {label}</span>'


def opp_badge(level: str) -> str:
    level = (level or "").lower()
    if level == "high":
        cls = "badge-opp-high"; label = "HIGH"
    elif level == "medium":
        cls = "badge-opp-medium"; label = "MEDIUM"
    else:
        cls = "badge-opp-low"; label = "LOW"
    return f'<span class="badge {cls}">Opportunity: {label}</span>'


def severity_icon(sev: float) -> str:
    if sev is None:
        return "🟢"
    if sev >= 0.7:
        return "🔴"
    if sev >= 0.4:
        return "🟠"
    if sev >= 0.2:
        return "🟡"
    return "🟢"


# --------------------------------------------------------------------
# IMPACT CALCULATION HELPERS (mirrors score.py logic)
# --------------------------------------------------------------------
def location_factor(industry: str, event_districts):
    if not event_districts or event_districts == ["NATIONAL"]:
        return 0.6
    industry_provinces = INDUSTRY_REGIONS.get(industry, [])
    max_factor = 0.1
    for district in event_districts:
        province = district_to_province(district)
        if not province:
            continue
        if province in industry_provinces:
            max_factor = max(max_factor, 1.0)
        else:
            max_factor = max(max_factor, 0.3)
    return max_factor


def event_impact_for_industry(event, industry: str):
    """Approximate per-event impact for selected industry (for explanation only)."""
    if not SENSITIVITY_MATRIX:
        return None

    etype = event.get("event_type")
    sev = event.get("severity", 0) or 0
    districts = event.get("districts", ["NATIONAL"])

    if not etype or etype not in SENSITIVITY_MATRIX:
        return None

    sens = SENSITIVITY_MATRIX[etype].get(industry)
    if sens is None:
        return None

    loc_factor = location_factor(industry, districts)
    impact = (sev * sens * loc_factor) / 2

    # exposure corrections (same logic as score.py)
    if industry == "IT":
        impact *= 0.3
    if industry == "Banking":
        impact *= 0.5
    if industry == "Energy":
        impact *= 0.7
    if industry == "Tourism":
        impact *= 0.8
    if industry == "Agriculture":
        impact *= 1.2
    if industry == "Water":
        impact *= 1.2
    if industry == "Retail":
        impact *= 0.9

    return impact


# --------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------
def render_header():
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown(
            "<h2 style='color:white;'>🌙 Sri Lanka Industry Risk Intelligence Dashboard</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color:#9DA5B4; font-size:0.9rem;'>Real-time socio-economic and operational signals interpreted for Sri Lankan industries.</p>",
            unsafe_allow_html=True,
        )
    with col2:
        last_mtime = get_file_mtime("data/processed/industry_scores.json")
        st.markdown(
            f"""
            <div style="text-align:right; font-size:0.8rem; color:#9DA5B4;">
                Auto-refresh: every 5 minutes<br/>
                Last updated: <b>{last_mtime or "N/A"}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("<hr style='border-color:#21262D;'/>", unsafe_allow_html=True)


# --------------------------------------------------------------------
# TAB 1: OVERVIEW
# --------------------------------------------------------------------
def overview_tab(industry_scores):
    st.markdown(
        "<div class='section-title'>📊 Industry Risk & Opportunity Overview</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='section-subtitle'>Snapshot of current risk and opportunity across key Sri Lankan industries.</div>",
        unsafe_allow_html=True,
    )

    if not industry_scores:
        st.warning("No industry scores found. Run your scoring pipeline first.")
        return

    rows = []
    for ind, data in industry_scores.items():
        if ind == "last_updated":
            continue
        rows.append({
            "Industry": ind,
            "Risk Score": round(float(data.get("risk_score", 0)), 2),
            "Risk Level": data.get("risk_level", "Low"),
            "Opportunity Score": round(float(data.get("opp_score", 0)), 2),
            "Opportunity Level": data.get("opp_level", "Low"),
            "Top Driver": (data.get("top_drivers") or ["-"])[0],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)


# --------------------------------------------------------------------
# TAB 2: INDUSTRY DETAILS
# --------------------------------------------------------------------
def industry_details_tab(industry_scores, events):
    if not industry_scores:
        st.warning("No industry scores found.")
        return

    industries = [k for k in industry_scores.keys() if k != "last_updated"]
    if not industries:
        st.warning("No industries in scores file.")
        return

    selected = st.selectbox("Select industry", industries)

    data = industry_scores[selected]

    st.markdown(
        f"<div class='section-title'>🏭 Industry: {selected}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='section-subtitle'>Drill-down of how current events translate into risk and opportunity for this industry.</div>",
        unsafe_allow_html=True,
    )

    risk_score = float(data.get("risk_score", 0) or 0)
    opp_score = float(data.get("opp_score", 0) or 0)
    risk_level = data.get("risk_level", "Low")
    opp_level = data.get("opp_level", "Low")
    drivers = data.get("top_drivers") or []

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Risk Score", f"{risk_score:.2f}")
        st.markdown(risk_badge(risk_level), unsafe_allow_html=True)
    with c2:
        st.metric("Opportunity Score", f"{opp_score:.2f}")
        st.markdown(opp_badge(opp_level), unsafe_allow_html=True)

    st.markdown("<br/><div class='section-title'>⚠ Top Driver Events</div>", unsafe_allow_html=True)
    if not drivers:
        st.info("No driver events recorded for this industry.")
    else:
        for idx, title in enumerate(drivers, start=1):
            st.markdown(
                f"<div style='margin-bottom:0.3rem; font-size:0.9rem;'><b>{idx}️⃣ {title}</b></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br/><div class='section-title'>📊 Event Impact Table</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Events are ordered by how strongly they are estimated to impact this industry (risk or opportunity).</div>",
        unsafe_allow_html=True,
    )

    impact_rows = []
    for ev in events:
        impact = event_impact_for_industry(ev, selected)
        if impact is None:
            continue
        impact_rows.append({
            "Event Title": ev.get("title", "")[:120],
            "Type": ev.get("event_type", ""),
            "Districts": ", ".join(ev.get("districts") or []),
            "Severity": round(float(ev.get("severity", 0) or 0), 2),
            "Impact": round(float(impact), 4),
        })

    if not impact_rows:
        st.info("No events with computable impact for this industry yet.")
    else:
        impact_rows = sorted(impact_rows, key=lambda r: abs(r["Impact"]), reverse=True)
        st.dataframe(pd.DataFrame(impact_rows), use_container_width=True)


# --------------------------------------------------------------------
# TAB 3: EVENTS FEED
# --------------------------------------------------------------------
def events_tab(events):
    st.markdown(
        "<div class='section-title'>🔥 Live Event Feed</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='section-subtitle'>Newest classified events with severity and location, powering the industry risk model.</div>",
        unsafe_allow_html=True,
    )

    if not events:
        st.warning("No events found. Run your scrapers and classification pipeline.")
        return

    # sort by timestamp if present, else severity
    def event_sort_key(e):
        ts = e.get("timestamp") or ""
        sev = float(e.get("severity", 0) or 0)
        return (ts, sev)

    # show most recent first
    events_sorted = sorted(events, key=event_sort_key, reverse=True)

    for ev in events_sorted[:200]:
        title = ev.get("title", "Untitled event")
        etype = ev.get("event_type", "Unknown")
        sev = float(ev.get("severity", 0) or 0)
        districts = ev.get("districts") or []
        src = ev.get("source_type", "unknown")
        ts = ev.get("timestamp", "")
        icon = severity_icon(sev)

        st.markdown("<div class='event-row'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='event-title'>{icon} [{sev:.2f}] {title}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='event-meta'>"
            f"Type: <b>{etype}</b> &nbsp;&nbsp; "
            f"Districts: {', '.join(districts) or 'N/A'} &nbsp;&nbsp; "
            f"Source: {src} &nbsp;&nbsp; "
            f"Time: {ts or 'N/A'}"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------------
# TAB 4: DYNAMIC EVENT–INDUSTRY IMPACT MATRIX
# --------------------------------------------------------------------
def matrix_tab(events):
    st.markdown(
        "<div class='section-title'>📐 Event → Industry Impact Matrix</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='section-subtitle'>Average estimated impact of each event type on each industry, based on recent events.</div>",
        unsafe_allow_html=True,
    )

    if not events or not SENSITIVITY_MATRIX:
        st.info("Need both events and sensitivity matrix to build matrix.")
        return

    if not INDUSTRIES:
        # fallback: infer industries from sensitivity matrix keys
        inferred_inds = set()
        for et in SENSITIVITY_MATRIX.values():
            inferred_inds.update(list(et.keys()))
        industries = sorted(list(inferred_inds))
    else:
        industries = INDUSTRIES

    # Collect impacts: (event_type, industry) -> list of impacts
    impacts = {}
    for ev in events:
        etype = ev.get("event_type")
        if not etype:
            continue
        for ind in industries:
            imp = event_impact_for_industry(ev, ind)
            if imp is None:
                continue
            impacts.setdefault((etype, ind), []).append(imp)

    if not impacts:
        st.info("No computable event impacts to show in matrix.")
        return

    # Build matrix
    all_event_types = sorted({k[0] for k in impacts.keys()})
    matrix = []
    for et in all_event_types:
        row = {"Event Type": et}
        for ind in industries:
            key = (et, ind)
            vals = impacts.get(key)
            if not vals:
                row[ind] = ""
            else:
                avg = sum(vals) / len(vals)
                row[ind] = round(avg, 3)
        matrix.append(row)

    df = pd.DataFrame(matrix)
    st.dataframe(df, use_container_width=True)


# --------------------------------------------------------------------
# TAB 5: INTERACTIVE MAP
# --------------------------------------------------------------------
def map_tab(events):
    st.markdown(
        "<div class='section-title'>🗺 Sri Lanka Event Map</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='section-subtitle'>Geospatial view of recent events by district and severity.</div>",
        unsafe_allow_html=True,
    )

    if not events:
        st.warning("No events to display on the map.")
        return

    # Build dataframe for map
    map_rows = []
    for ev in events:
        districts = ev.get("districts") or []
        if not districts:
            continue
        # take first district for map point
        d = districts[0]
        coords = DISTRICT_COORDS.get(d)
        if not coords:
            continue
        lat, lon = coords
        sev = float(ev.get("severity", 0) or 0)
        etype = ev.get("event_type", "Unknown")
        title = ev.get("title", "")
        map_rows.append(
            {
                "lat": lat,
                "lon": lon,
                "severity": sev,
                "event_type": etype,
                "title": title,
                "district": d,
            }
        )

    if not map_rows:
        st.info("No events with known district coordinates to map.")
        return

    df_map = pd.DataFrame(map_rows)

    # Color & radius based on severity
    df_map["radius"] = df_map["severity"].apply(lambda s: 5000 + 30000 * s)

    def sev_color(s):
        # higher severity → more red
        r = int(200 + 55 * s)
        g = int(120 * (1 - s))
        b = int(40 * (1 - s))
        return [r, g, b, 160]

    df_map["color"] = df_map["severity"].apply(sev_color)

    midpoint = (df_map["lat"].mean(), df_map["lon"].mean())

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position="[lon, lat]",
        get_radius="radius",
        get_color="color",
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=6.7,
        pitch=0,
    )

    tool_tip = {
        "html": "<b>{event_type}</b><br/>{title}<br/>District: {district}<br/>Severity: {severity}",
        "style": {"backgroundColor": "rgba(22,27,34,0.9)", "color": "white"},
    }

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tool_tip,
            map_style="mapbox://styles/mapbox/dark-v10",
        )
    )


# --------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------
def main():
    render_header()

    industry_scores = load_industry_scores()
    events = load_events()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Overview", "Industry Details", "Events", "Matrix", "Map"]
    )

    with tab1:
        overview_tab(industry_scores)

    with tab2:
        industry_details_tab(industry_scores, events)

    with tab3:
        events_tab(events)

    with tab4:
        matrix_tab(events)

    with tab5:
        map_tab(events)


if __name__ == "__main__":
    main()
