import requests
import feedparser
import json
from datetime import datetime
from src.scrapers import yt_key

from pathlib import Path   
from bs4 import BeautifulSoup

def save_with_limited_history(path, new_items, max_items=8000):

    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    combined = existing + new_items

    # Remove duplicates (based on URL)
    seen = set()
    unique = []
    for it in combined:
        uid = it.get("url") or it.get("link")
        if uid and uid not in seen:
            seen.add(uid)
            unique.append(it)

    # Keep only the LAST max_items
    unique = unique[-max_items:]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

    print(f"[+] Stored {len(unique)} items → {path}")

# ----------------------------------------------
# CONFIG
# ----------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SL-AwarenessBot/1.0)"
}
OUTPUT_FILE = "data/raw/sri_lanka_news.json"

YOUTUBE_API_KEY = yt_key.YOUTUBE  # free quota

# RSS sources (Sri Lanka)
RSS_FEEDS = [
    "https://www.adaderana.lk/rss/latest_news",
    "https://www.hirunews.lk/rss/english.xml",
    "https://colombogazette.com/feed/",
    "https://economynext.com/feed/",
    "https://www.newsfirst.lk/feed/",
    "https://www.dailynews.lk/feed/",
    "https://www.dailymirror.lk/rss",
    "https://www.sundaytimes.lk/feed/",
    "https://ceylontoday.lk/feed/",
    "https://www.news.lk/rss",
    "https://www.parliament.lk/en/news-feed",
     "https://www.slguardian.org/feed/",
    "https://www.timesonline.lk/feed/",
    "https://www.themorning.lk/feed/",
    "https://www.virakesari.lk/rss",
    "https://www.uthayan.lk/feed",
    "https://www.dinakaran.com/rss",
    "https://www.sudaroli.lk/feed",
    "https://news.google.com/rss/search?q=Sri+Lanka",
    "https://news.google.com/rss/search?q=Sri+Lanka+economy",
    "https://news.google.com/rss/search?q=Sri+Lanka+politics",
    "https://news.google.com/rss/search?q=Colombo",
    "https://news.google.com/rss/search?q=South+Asia",


]

# Google News RSS for Sri Lanka
GOOGLE_NEWS_RSS = [
    "https://news.google.com/rss/search?q=Sri+Lanka&hl=en&gl=LK&ceid=LK:en",
    "https://news.google.com/rss/search?q=Sri+Lanka+economy&hl=en&gl=LK&ceid=LK:en",
    "https://news.google.com/rss/search?q=Sri+Lanka+government&hl=en&gl=LK&ceid=LK:en",
]

# YouTube Sri Lankan news channels
YOUTUBE_CHANNELS = [
    "UCNwz7hM0USJgd59jSPTcX5Q",  # Ada Derana
    "UC0hHx5j2jQD1nZ4YslcIFPA",  # Hiru News
    "UC7wfilQIdG6m4aJRZ3t0uCQ",  # NewsFirst
    "UCm6VPcWn3U-IvfQeSeQk5Ww",  # Sirasa TV
]

HTML_NEWS_SITES = [
    {"name": "Ada Derana", "url": "https://www.adaderana.lk/news", "selector": ".news-story h2 a"},
    {"name": "Hiru News", "url": "https://www.hirunews.lk/english", "selector": ".news-item a"},
    {"name": "NewsFirst", "url": "https://www.newsfirst.lk/latest", "selector": ".nf-latest-news a"},
    {"name": "DailyMirror", "url": "https://www.dailymirror.lk/latest_news", "selector": ".latest-news-list a"},
    {"name": "ColomboPage", "url": "https://colombopage.com/", "selector": "a"},
    {"name": "EconomyNext", "url": "https://economynext.com/", "selector": "h3 a"},
]

# ----------------------------------------------
# 1. RSS PARSER
# ----------------------------------------------
def scrape_rss():
    print("[+] Fetching RSS feeds...")
    all_news = []

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                summary = (
                entry.get("summary")
                or entry.get("description")
                or (entry.get("content", [{}])[0].get("value") if entry.get("content") else None)
                or ""
                )

                all_news.append({
                    "source": "rss",
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", None),
                    "summary": summary.strip(),
                    "content": summary.strip()      # content fallback
                })

        except Exception as e:
            print("RSS error:", e)
    return all_news


# ----------------------------------------------
# 2. GOOGLE NEWS RSS
# ----------------------------------------------
def scrape_google_news():
    print("[+] Fetching Google News...")
    data = []
    for url in GOOGLE_NEWS_RSS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
               summary = (
                entry.get("summary")
                or entry.get("description")
                or ""
            )

            data.append({
                "source": "google_news",
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", None),
                "summary": summary.strip(),
                "content": summary.strip()
            })

        except:
            pass
    return data


# ----------------------------------------------
# 3. YouTube News Headlines
# ----------------------------------------------
def scrape_youtube():
    print("[+] Fetching YouTube news...")
    results = []

    for channel_id in YOUTUBE_CHANNELS:
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?key={YOUTUBE_API_KEY}"
            f"&channelId={channel_id}"
            "&part=snippet&id"
            "&order=date"
            "&maxResults=50"
        )
        try:
            r = requests.get(url).json()

            if "items" in r:
                for item in r["items"]:
                    title = item["snippet"]["title"]
                    video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}" if "videoId" in item.get("id", {}) else None
                    
                    results.append({
                        "source": "youtube",
                        "title": title,
                        "link": video_url,
                        "published": item["snippet"]["publishedAt"],
                        "summary": item["snippet"].get("description", f"YouTube news: {title}"),
                        "content": item["snippet"].get("description", f"YouTube news: {title}")
                    })

        except:
            pass

    return results


# ----------------------------------------------
# 4. GDELT Global News Filter for Sri Lanka
# ----------------------------------------------
def scrape_gdelt():
    print("[+] Fetching GDELT data...")

    url = "http://api.gdeltproject.org/api/v2/doc/doc?query=Sri%20Lanka&mode=ArtList&format=json&maxrecords=250"
    try:
        data = requests.get(url).json()
        articles = data.get("articles", [])
        result = []

        for a in articles:
           result.append({
                "source": "gdelt",
                "title": a.get("title"),
                "link": a.get("url"),
                "published": a.get("seendate"),
                "summary": a.get("summary", a.get("snippet", "")),
                "content": a.get("content", "")
            })

        return result
    except:
        return []


# -----------------------------------------------------
# (REMOVED) REDDIT API — COMMENTED OUT
# -----------------------------------------------------

"""
# import praw

def scrape_reddit():
    print("[+] Fetching Reddit (DISABLED — Approval Required)")

    reddit = praw.Reddit(
        client_id="YOUR_ID",
        client_secret="YOUR_SECRET",
        user_agent="SLNewsCollector by u/YOURNAME"
    )

    subreddits = ["srilanka", "SriLankaNews", "SriLankaPolitics"]

    data = []
    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        for post in subreddit.hot(limit=100):
            data.append({
                "source": "reddit",
                "title": post.title,
                "link": f"https://reddit.com{post.permalink}",
                "published": datetime.utcfromtimestamp(post.created_utc).isoformat(),
            })
    return data
"""
def fetch_html_pages(base_url, selector, pages=3):
    results = []
    for p in range(1, pages+1):
        url = f"{base_url}?page={p}"
        try:
            print("[HTML]", url)
            resp = requests.get(url, headers=HEADERS, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup.select(selector):
                title = tag.text.strip()
                link = tag.get("href")
                if link.startswith("/"):
                    link = base_url.rstrip("/") + link
                results.append({"title": title, "link": link})
        except:
            continue
    return results


# -----------------------------------------------------
# MASTER AGGREGATOR
# -----------------------------------------------------
def main():
    print("================================")
    print("   SRI LANKA NEWS SCRAPER")
    print("   (Reddit Removed)")
    print("================================")

    combined = []

    combined += scrape_rss()
    combined += scrape_google_news()
    combined += scrape_youtube()
    combined += scrape_gdelt()

    # Future:
    # combined += scrape_reddit()   # re-enable when approved

    print(f"\n[✓] Total collected: {len(combined)} headlines")

    save_with_limited_history(OUTPUT_FILE, combined)


    print(f"[✓] Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()