import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pathlib import Path   

# ===============================
#   GLOBAL OPTIMIZATION CONFIG
# ===============================

TIMEOUT = 5
MAX_ITEMS_PER_SOURCE = 30
MAX_SUMMARY_LENGTH = 400

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SL-AwarenessBot/1.0)"
}

OUTPUT_FILE = Path("data/raw/government_news.json")


# ===============================
#   STORAGE (FAST + SAFE)
# ===============================

def save_with_limited_history(path, new_items, max_items=8000):
    """Store history safely and limit size."""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
        except:
            existing = []
    else:
        existing = []

    combined = existing + new_items

    # Deduplicate using URL
    seen = set()
    unique = []
    for item in combined:
        uid = item.get("url")
        if uid and uid not in seen:
            seen.add(uid)
            unique.append(item)

    # Limit size
    unique = unique[-max_items:]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

    print(f"[✓] Stored {len(unique)} items → {path}")


# ===============================
#   GOVERNMENT SOURCES (FIXED)
# ===============================

GOV_SOURCES = [
    # Disaster, Weather, Alerts
    {"name": "Disaster Management Centre",
     "url": "https://www.dmc.gov.lk/index.php?format=feed&type=rss",
     "type": "rss"},

    {"name": "Met Department Weather Alerts",
     "url": "https://meteo.gov.lk/index.php?option=com_content&view=category&id=34&Itemid=592&format=feed&type=rss",
     "type": "rss"},

    {"name": "Irrigation Department Alerts",
     "url": "https://www.irrigation.gov.lk/index.php?option=com_content&view=category&id=12&Itemid=208&format=feed&type=rss",
     "type": "rss"},

    # Main Gov Portals (FIXED: Now using RSS!)
    {"name": "News.lk",
     "url": "https://www.news.lk/component/k2/itemlist?format=feed&type=rss",
     "type": "rss"},

    {"name": "DGI",
     "url": "https://www.dgi.gov.lk/index.php?format=feed&type=rss",
     "type": "rss"},

    # Finance / Economy
    {"name": "Central Bank Sri Lanka",
     "url": "https://www.cbsl.gov.lk/en/news/what_s_new",
     "type": "html",
     "selector": ".view-content .views-row a"},

    {"name": "Import Export Control",
     "url": "http://www.imexport.gov.lk/web/index.php/en/notifications?format=feed&type=rss",
     "type": "rss"},

    # Health
    {"name": "Ministry of Health",
     "url": "https://www.health.gov.lk/rss/",
     "type": "rss"},

    {"name": "Epidemiology Unit",
     "url": "http://www.epid.gov.lk/web/index.php?option=com_content&view=category&id=201&Itemid=449&lang=en&format=feed&type=rss",
     "type": "rss"},

    # Transport / Police / Parliament
    
    {"name": "Parliament News",
     "url": "https://www.parliament.lk/en/news-feed",
     "type": "rss"},
]


# ===============================
#   RSS EXTRACTOR (Fast + Accurate)
# ===============================

def extract_rss(source):
    print(f"[RSS] {source['name']}")
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(resp.text, "xml")

        items = []
        for i, item in enumerate(soup.find_all("item")):
            if i >= MAX_ITEMS_PER_SOURCE:
                break

            summary = item.description.text if item.description else ""

            items.append({
                "title": item.title.text.strip() if item.title else None,
                "url": item.link.text.strip() if item.link else None,
                "summary": summary.strip(),
                "published": item.pubDate.text if item.pubDate else None,
                "source": source["name"],
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "timestamp": (
                item.pubDate.text if item.pubDate else datetime.now(timezone.utc).isoformat()
    ),
            })

        return items

    except Exception as e:
        print(f"[RSS ERROR] {source['name']} → {e}")
        return []


# ===============================
#   UNIVERSAL HTML SUMMARY EXTRACTOR
# ===============================

def extract_html_summary(url):
    """Universal summary extractor for all Sri Lankan gov websites."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=7)
        soup = BeautifulSoup(resp.text, "html.parser")

        # 1 — Known CMS structures
        CMS_SELECTORS = [
            "div.itemFullText",         # News.lk
            "div.article-content",      # DGI
            "div.field-item",           # CBSL
            "div.entry-content",        # Health (WordPress)
            "div#content",              # Epidemiology Unit
            "article",                  # General articles
            "section.content-section",  # Parliament
            "div.post-content",
            "div.content",
            "div.text-content",
            "div.main-content",
            "div.col-md-8",
            "div.col-lg-8",
            "div.td-post-content",
        ]

        for selector in CMS_SELECTORS:
            block = soup.select_one(selector)
            if block:
                text = block.get_text(" ", strip=True)
                if len(text) > 30:  # ensure real content
                    return text[:MAX_SUMMARY_LENGTH]

        # 2 — Extract largest paragraph block
        paragraphs = soup.find_all("p")
        if paragraphs:
            longest = max(paragraphs, key=lambda p: len(p.get_text(strip=True)))
            txt = longest.get_text(" ", strip=True)
            if len(txt) > 30:
                return txt[:MAX_SUMMARY_LENGTH]

        # 3 — Extract from content divs
        divs = soup.find_all("div")
        if divs:
            largest = max(divs, key=lambda d: len(d.get_text(strip=True)))
            txt = largest.get_text(" ", strip=True)
            if len(txt) > 30:
                return txt[:MAX_SUMMARY_LENGTH]

        return ""

    except Exception:
        return ""


# ===============================
#   HTML EXTRACTOR (only for CBSL)
# ===============================

def extract_html(source):
    print(f"[HTML] {source['name']}")
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(resp.text, "html.parser")

        items = []
        links = soup.select(source.get("selector", "a"))

        for i, tag in enumerate(links):
            if i >= MAX_ITEMS_PER_SOURCE:
                break

            title = tag.text.strip()
            link = tag.get("href")
            if not title or not link:
                continue

            if link.startswith("/"):
                base = source["url"].rstrip("/")
                link = base + link

            summary = extract_html_summary(link)

            items.append({
                "title": title,
                "url": link,
                "summary": summary,
                "published": None,
                "source": source["name"],
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        return items

    except Exception as e:
        print(f"[HTML ERROR] {source['name']} → {e}")
        return []


# ===============================
#   MAIN EXECUTION
# ===============================

def run_gov_collector():
    all_items = []

    for source in GOV_SOURCES:
        if source["type"] == "rss":
            all_items += extract_rss(source)
        else:
            all_items += extract_html(source)

    save_with_limited_history(OUTPUT_FILE, all_items)


if __name__ == "__main__":
    run_gov_collector()
