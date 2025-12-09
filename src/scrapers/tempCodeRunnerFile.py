import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pathlib import Path   

# ===============================
#   GLOBAL OPTIMIZATION CONFIG
# ===============================

TIMEOUT = 5             # Faster timeout (5 sec)
MAX_ITEMS_PER_SOURCE = 20   # Do not fetch 200 links from slow sites
MAX_SUMMARY_LENGTH = 400
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SL-AwarenessBot/1.0)"
}

# ===============================
#   STORAGE (FAST + SAFE)
# ===============================

def save_with_limited_history(path, new_items, max_items=8000):
    """Efficiently store history while avoiding duplicates."""
    
    # Load existing
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

    # Combine
    combined = existing + new_items

    # Deduplication
    seen = set()
    unique = []
    for it in combined:
        uid = it.get("url")
        if uid and uid not in seen:
            seen.add(uid)
            unique.append(it)

    # Limit to last N items
    unique = unique[-max_items:]

    # Save
    with open(path, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

    print(f"[✓] Stored {len(unique)} items → {path}")


# ===============================
#   GOVERNMENT SOURCES
# ===============================

GOV_SOURCES = [
    # 1. Disaster / Weather / Alerts
    {"name": "Disaster Management Centre", "url": "https://www.dmc.gov.lk/index.php?format=feed&type=rss", "type": "rss"},
    {"name": "Met Department Weather Alerts", "url": "https://meteo.gov.lk/index.php?option=com_content&view=category&id=34&Itemid=592&format=feed&type=rss", "type": "rss"},
    {"name": "Irrigation Department Alerts", "url": "https://www.irrigation.gov.lk/index.php?option=com_content&view=category&id=12&Itemid=208&format=feed&type=rss", "type": "rss"},

    # 2. Main Gov Portals (FIXED)
    {"name": "News.lk", 
     "url": "https://www.news.lk/component/k2/itemlist?format=feed&type=rss", 
     "type": "rss"},

    {"name": "DGI", 
     "url": "https://www.dgi.gov.lk/index.php?format=feed&type=rss", 
     "type": "rss"},

    # 3. Finance / Economy
    {"name": "Central Bank", 
     "url": "https://www.cbsl.gov.lk/en/news/what_s_new", 
     "type": "html", "selector": ".view-content .views-row a"},

    {"name": "Import Export Control", 
     "url": "http://www.imexport.gov.lk/web/index.php/en/notifications?format=feed&type=rss", 
     "type": "rss"},

    # 4. Health
    {"name": "Ministry of Health", "url": "https://www.health.gov.lk/rss/", "type": "rss"},
    {"name": "Epidemiology Unit", "url": "http://www.epid.gov.lk/...&format=feed&type=rss", "type": "rss"},

    # 5. Transport / Police / Parliament
    {"name": "Sri Lanka Police", "url": "https://www.police.lk/...&format=feed&type=rss", "type": "rss"},
    {"name": "Parliament News", "url": "https://www.parliament.lk/en/news-feed", "type": "rss"},
]


OUTPUT_FILE = Path("data/raw/government_news.json")


# ===============================
#   RSS EXTRACTOR (Fast)
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

            items.append({
                "title": item.title.text.strip() if item.title else None,
                "url": item.link.text.strip() if item.link else None,
                "summary": item.description.text.strip() if item.description else "",
                "published": item.pubDate.text if item.pubDate else None,
                "source": source["name"],
                "fetched_at": datetime.now(timezone.utc).isoformat()
            })

        return items

    except Exception as e:
        print(f"[RSS ERROR] {source['name']} → {e}")
        return []


# ===============================
#   LIGHT HTML SCRAPER (Fast)
# ===============================

def extract_html_summary(url):
    """Universal summary extractor for all SL gov websites."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")

        # ---------------------------------------------------
        # 1. NEWS.LK (Joomla CMS)
        # ---------------------------------------------------
        block = soup.find("div", {"class": "itemFullText"})
        if block:
            text = block.get_text(" ", strip=True)
            return text[:MAX_SUMMARY_LENGTH]

        # ---------------------------------------------------
        # 2. DGI.gov.lk (Joomla)
        # ---------------------------------------------------
        block = soup.find("div", {"class": "article-content"})
        if block:
            text = block.get_text(" ", strip=True)
            return text[:MAX_SUMMARY_LENGTH]

        # ---------------------------------------------------
        # 3. CBSL (Drupal)
        # ---------------------------------------------------
        block = soup.find("div", {"class": "field-item"})
        if block:
            text = block.get_text(" ", strip=True)
            return text[:MAX_SUMMARY_LENGTH]

        # ---------------------------------------------------
        # 4. Ministry of Health (WordPress)
        # ---------------------------------------------------
        block = soup.find("div", {"class": "entry-content"})
        if block:
            text = block.get_text(" ", strip=True)
            return text[:MAX_SUMMARY_LENGTH]

        # ---------------------------------------------------
        # 5. Epidemiology Unit
        # ---------------------------------------------------
        block = soup.find("div", {"id": "content"})
        if block:
            text = block.get_text(" ", strip=True)
            return text[:MAX_SUMMARY_LENGTH]

        # ---------------------------------------------------
        # 6. Railway.gov.lk / Police.lk / Wildlife.gov.lk
        # ---------------------------------------------------
        block = soup.find("div", {"class": "content"})
        if block:
            text = block.get_text(" ", strip=True)
            return text[:MAX_SUMMARY_LENGTH]

        block = soup.find("div", {"class": "post-content"})
        if block:
            text = block.get_text(" ", strip=True)
            return text[:MAX_SUMMARY_LENGTH]

        # ---------------------------------------------------
        # 7. Parliament.lk
        # ---------------------------------------------------
        block = soup.find("section", {"class": "content-section"})
        if block:
            text = block.get_text(" ", strip=True)
            return text[:MAX_SUMMARY_LENGTH]

        # ---------------------------------------------------
        # 8. IMF / Treasury (articles)
        # ---------------------------------------------------
        block = soup.find("article")
        if block:
            text = block.get_text(" ", strip=True)
            return text[:MAX_SUMMARY_LENGTH]

        # ---------------------------------------------------
        # 9. GENERIC fallbacks for ANY gov website
        # ---------------------------------------------------
        # First paragraph
        p = soup.find("p")
        if p:
            return p.get_text(" ", strip=True)[:MAX_SUMMARY_LENGTH]

        # Any readable div
        div = soup.find("div")
        if div:
            return div.get_text(" ", strip=True)[:MAX_SUMMARY_LENGTH]

        return ""

    except:
        return ""



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
                "fetched_at": datetime.now(timezone.utc).isoformat()
            })

        return items

    except Exception as e:
        print(f"[HTML ERROR] {source['name']} → {e}")
        return []


# ===============================
#   MAIN RUNNER
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
