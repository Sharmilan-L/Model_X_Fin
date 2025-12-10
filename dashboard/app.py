import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pydeck as pdk
import numpy as np
from pathlib import Path
from textwrap import dedent
import re

# ----------------------------------------------------
# Helpers
# ----------------------------------------------------
def clean_html(text: str) -> str:
    """Remove HTML tags from summaries."""
    if not isinstance(text, str):
        return ""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text).strip()


st.set_page_config(page_title="Sri Lanka Dashboard", layout="wide")

EVENTS_FILE = "data/processed/events.json"
DISTRICT_FILE = "data/processed/district_scores.json"

# ----------------------------------------------------
# Load Data
# ----------------------------------------------------
def load_events() -> pd.DataFrame:
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        events = json.load(f)
    return pd.DataFrame(events)


def load_district_scores() -> pd.DataFrame | None:
    path = Path(DISTRICT_FILE)
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # handle dict {"Colombo": {...}, ...}
    if isinstance(raw, dict):
        rows = []
        for name, info in raw.items():
            row = {"district": name}
            row.update(info)
            rows.append(row)
        return pd.DataFrame(rows)

    # already list of dicts
    return pd.DataFrame(raw)


df = load_events()
district_df = load_district_scores()

# ----------------------------------------------------
# CREATE TABS
# ----------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🌍 National Overview", "📍 District Insights",
     "🏭 Industry Insights", "📰 Event Explorer", "🎯 Recommendations"]
)

# ----------------------------------------------------
# =======================
#        TAB 1
# =======================
# ----------------------------------------------------
with tab1:
    st.title("🇱🇰 Sri Lanka — National Situation Overview")

    last_time = df["timestamp"].max()
    st.caption(f"Last Updated: **{last_time}**")
    st.markdown("---")

    # ------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    total_events = len(df)
    severe_events = len(df[df["severity"] > 0.6])
    affected_districts = df["districts"].explode().nunique()
    active_categories = df["event_type"].nunique()

    col1.metric("📡 Total Events (24h)", total_events)
    col2.metric("🔥 Severe Events", severe_events)
    col3.metric("📍 Districts Affected", affected_districts)
    col4.metric("🏷️ Categories Active", active_categories)

    # ------------------------------------------------
    # RISK MAP
    # ------------------------------------------------
    st.markdown("### 🗺️ District Risk Heatmap (From Model Scores)")

    if district_df is not None and not district_df.empty:
        risk_df = district_df.copy()

        # Ensure required columns exist
        for col in ["risk_score", "opp_score", "event_count"]:
            if col not in risk_df:
                risk_df[col] = 0

        risk_df["risk_score"] = pd.to_numeric(
            risk_df["risk_score"], errors="coerce"
        ).fillna(0.0)

        district_coords = {
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
            "Kegalle": (7.2513, 80.3464),
        }

        risk_df["lat"] = risk_df["district"].apply(
            lambda d: district_coords.get(d, (0, 0))[0]
        )
        risk_df["lon"] = risk_df["district"].apply(
            lambda d: district_coords.get(d, (0, 0))[1]
        )

        def risk_color(score: float) -> list[int]:
            if score >= 0.75:
                return [255, 0, 0]
            if score >= 0.55:
                return [255, 165, 0]
            if score >= 0.35:
                return [255, 255, 0]
            if score >= 0.20:
                return [144, 238, 144]
            return [0, 128, 0]

        risk_df["color"] = risk_df["risk_score"].apply(risk_color)
        risk_df["radius"] = risk_df["risk_score"] * 15000 + 3000

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=risk_df,
            get_position="[lon, lat]",
            get_radius="radius",
            get_fill_color="color",
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=7.8731, longitude=80.7718, zoom=6.8
        )

        tooltip = {
            "html": (
                "<b>{district}</b><br/>"
                "Risk: {risk_score}<br/>"
                "Opportunity: {opp_score}<br/>"
                "Events: {event_count}"
            ),
            "style": {"backgroundColor": "black", "color": "white"},
        }

        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip,
            ),
            key="district_risk_map",
        )

    st.markdown("---")

    # ------------------------------------------------
    # DONUT CHART – EVENT CATEGORY
    # ------------------------------------------------
    st.markdown("### 🧩 Breakdown by Event Category")

    category_count = df["event_type"].value_counts()

    fig_cat = px.pie(
        values=category_count.values,
        names=category_count.index,
        hole=0.45,
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    # ------------------------------------------------
    # BAR – EVENT SOURCE DISTRIBUTION
    # ------------------------------------------------
    st.markdown("### 📊 Event Source Distribution")

    source_count = df["source_type"].value_counts().reset_index()
    source_count.columns = ["source_type", "count"]

    fig_src = px.bar(
        source_count,
        x="source_type",
        y="count",
        text="count",
        title="Events by Source Type",
        color="source_type",
    )

    fig_src.update_layout(
        xaxis_title="Source Type",
        yaxis_title="Number of Events",
        showlegend=False,
    )

    st.plotly_chart(fig_src, use_container_width=True, key="event_source_bar")

    # ------------------------------------------------
    # TOP NEWS ALERTS (CARDS)
    # ------------------------------------------------
    st.markdown("### 📰 Top News Alerts")

    # Filter only news-like sources
    news_df = df[df["source_type"].str.contains("news", case=False, na=False)].copy()

    # Prefer 'published' if present, else fallback to 'timestamp'
    def get_publish_time(row):
        return row.get("published") or row.get("timestamp")

    news_df["published_final"] = news_df.apply(get_publish_time, axis=1)
    news_df["published_parsed"] = pd.to_datetime(
        news_df["published_final"], errors="coerce", utc=True
    )

    # Keep only last 48 hours
    cutoff = pd.Timestamp.utcnow() - pd.Timedelta(hours=48)
    news_df = news_df[news_df["published_parsed"] >= cutoff]

    # Latest 20 news items
    critical = news_df.sort_values(
        "published_parsed", ascending=False
    ).head(20)

    if len(critical) == 0:
        st.info("No recent news available.")
    else:
        for _, row in critical.iterrows():
            # Human readable time
            try:
                ts = pd.to_datetime(row["published_final"], utc=True)
                diff = pd.Timestamp.utcnow() - ts
                hours = int(diff.total_seconds() // 3600)

                if hours < 1:
                    time_label = "Just now"
                elif hours < 24:
                    time_label = f"{hours}h ago"
                else:
                    time_label = f"{hours // 24}d ago"
            except Exception:
                time_label = "Unknown"

            # Clean + trim summary
            summary_raw = row.get("summary", "")
            summary_clean = clean_html(summary_raw)
            if len(summary_clean) > 160:
                summary_clean = summary_clean[:160] + "..."

            url = row.get("url", "#")

            card_html = f"""
<div style="border:1px solid #333;
            border-radius:8px;
            padding:15px;
            margin:14px 0;
            background:rgba(255,255,255,0.06);">
  <h4 style="color:white; margin:0 0 8px 0;">
    📰 {row['title']}
  </h4>

  <p style="color:#aaa; margin:0 0 8px 0;">
    <b>Severity:</b> {row['severity']:.2f} &nbsp;|&nbsp;
    <b>Published:</b> {time_label}
  </p>

  <p style="color:#ddd; font-size:0.9em; margin:0 0 10px 0;">
    {summary_clean}
  </p>

  <a href="{url}" target="_blank"
     style="color:#4da6ff; text-decoration:none; font-size:0.9em;">
    🔗 Read full article
  </a>
</div>
"""
            card_html = dedent(card_html)
            st.markdown(card_html, unsafe_allow_html=True)

# ----------------------------------------------------
# =======================
#        TAB 2
# =======================
# ----------------------------------------------------
with tab2:
    st.title("📍 District Insights")

    if district_df is None or district_df.empty:
        st.warning("District score data not available.")
        st.stop()

    # ---- PICK DISTRICT ----
    district_names = district_df["district"].tolist()
    selected = st.selectbox("Select a District", district_names)

    # Extract selected row as dict
    row = district_df[district_df["district"] == selected].iloc[0].to_dict()

    # ---- HIGH LEVEL SUMMARY ----
    st.subheader(f"📊 Overview — {selected}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Score", f"{row.get('risk_score', 0):.2f}")
    c2.metric("Opportunity Score", f"{row.get('opp_score', 0):.2f}")
    c3.metric("Event Count", row.get("event_count", 0))

    st.markdown("---")

    # ----------------------------------------------------
    # 📉 RISK BAR CHART
    # ----------------------------------------------------
    st.subheader("📉 Risk Scores by Industry")

    industries = []
    risk_values = []

    skip_fields = {"district", "risk_score", "opp_score", 
                   "risk_level", "opp_level", "event_count"}

    for key, value in row.items():
        if key in skip_fields:
            continue
        if isinstance(value, dict) and "risk_score" in value:
            industries.append(key)
            risk_values.append(value["risk_score"])

    # Add overall district risk as first bar
    industries.insert(0, "Overall District Risk")
    risk_values.insert(0, row.get("risk_score", 0))

    risk_df = pd.DataFrame({
        "Category": industries,
        "Risk Score": risk_values
    })

    fig_risk = px.bar(
        risk_df,
        x="Category",
        y="Risk Score",
        text="Risk Score",
        range_y=[0, 1],
        title="Risk Score Breakdown",
        color="Risk Score",
        color_continuous_scale=["green", "yellow", "red"]
    )

    fig_risk.update_layout(xaxis_title="", yaxis_title="Risk Score")
    st.plotly_chart(fig_risk, use_container_width=True)

    st.markdown("---")

    # ----------------------------------------------------
    # 📈 OPPORTUNITY BAR CHART
    # ----------------------------------------------------
    st.subheader("📈 Opportunity Scores by Industry")

    industries2 = []
    opp_values = []

    for key, value in row.items():
        if key in skip_fields:
            continue
        if isinstance(value, dict) and "opp_score" in value:
            industries2.append(key)
            opp_values.append(value["opp_score"])

    # Add district-level opportunity score
    industries2.insert(0, "Overall District Opportunity")
    opp_values.insert(0, row.get("opp_score", 0))

    opp_df = pd.DataFrame({
        "Category": industries2,
        "Opportunity Score": opp_values
    })

    fig_opp = px.bar(
        opp_df,
        x="Category",
        y="Opportunity Score",
        text="Opportunity Score",
        range_y=[0, 1],
        title="Opportunity Score Breakdown",
        color="Opportunity Score",
        color_continuous_scale=["red", "yellow", "green"]
    )

    fig_opp.update_layout(xaxis_title="", yaxis_title="Opportunity Score")
    st.plotly_chart(fig_opp, use_container_width=True)

    st.markdown("---")

    # ----------------------------------------------------
    # 🧠 AI SUMMARY
    # ----------------------------------------------------
    st.subheader("🧠 AI Summary")

    risk_score = row.get("risk_score", 0)
    opp_score = row.get("opp_score", 0)
    risk_level = row.get("risk_level", "Unknown")
    opp_level = row.get("opp_level", "Unknown")
    ev_count = row.get("event_count", 0)

    summary = f"""
### 📌 Summary for **{selected}**

- **Risk Level:** {risk_level} ({risk_score:.2f})
- **Opportunity Level:** {opp_level} ({opp_score:.2f})
- **Events Analyzed:** {ev_count}

{selected} currently shows a **{risk_level.lower()} risk profile**, while opportunity trends indicate **{opp_level.lower()} potential** for operations, investment, and socio-economic activity.
"""

    st.markdown(summary)


with tab3:
    st.title("🏭 Industry Insights")
    st.info("➡ Industry-specific analysis for Sri Lanka. (Coming next)")

# ----------------------------------------------------
# =======================
#        TAB 4
# =======================
# ----------------------------------------------------
with tab4:
    st.title("📰 Event Explorer")
    st.info("➡ A searchable filterable event explorer. (Coming next)")

# ----------------------------------------------------
# =======================
#        TAB 5
# =======================
# ----------------------------------------------------
with tab5:
    st.title("🎯 Recommendations Center")
    st.info("➡ AI-generated recommendations for government, industries, and public. (Coming next)")
