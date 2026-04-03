import feedparser
import requests
import re
from ddgs import DDGS
from concurrent.futures import ThreadPoolExecutor, as_completed

RSS_FEEDS = [
    # ===== INDIAN NATIONAL NEWS =====
    "https://www.ndtv.com/rss/top-stories",
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://www.thehindu.com/feeder/default.rss",
    "https://indianexpress.com/feed/",
    "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    "https://www.news18.com/rss/india.xml",
    "https://zeenews.india.com/rss/india-national-news.xml",
    "https://aajtak.in/rssfeeds/?id=home",
    "https://www.republicworld.com/rss/india-news.xml",
    "https://ddnews.gov.in/en/feeds/news",

    # ===== FACT CHECK (Most Important!) =====
    "https://www.altnews.in/feed/",
    "https://www.boomlive.in/feed",
    "https://factcheck.afp.com/rss",
    "https://www.vishvasnews.com/feed/",

    # ===== KARNATAKA =====
    "https://www.deccanherald.com/rss-feed/feed",
    "https://www.prajavani.net/feed",
    "https://www.udayavani.com/feed",
    "https://kannada.oneindia.com/rss/",
    "https://www.newskarnataka.com/feed",
    "https://www.sahilonline.org/feed",

    # ===== INDIAN GOVERNMENT OFFICIAL =====
    "https://pib.gov.in/rss.aspx",
    "https://www.rbi.org.in/Scripts/RSS.aspx?Id=1",
    "https://www.isro.gov.in/rss.xml",
    "https://www.mea.gov.in/press-releases.html?rss=1",

    # ===== INTERNATIONAL =====
    "https://www.wionews.com/feeds",
    "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?d=world",
    "https://sputnikglobe.com/world/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.reuters.com/reuters/topNews",

    # ===== HEALTH & SCIENCE =====
    "https://www.who.int/feeds/entity/csr/don/en/rss.xml",
    "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.atom",

    # ===== TECHNOLOGY & CYBER =====
    "https://techcrunch.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://feeds.arstechnica.com/arstechnica/index",

    # ===== WORLD AFFAIRS =====
    "https://www.weforum.org/agenda/feed/",
    "https://www.un.org/en/feed/announcements/rss.xml",
    "https://www.worldbank.org/en/news/all/rss.xml",
]
def extract_keywords(text: str) -> list:
    stopwords = {
        "is", "the", "of", "and", "a", "an", "in", "on", "at",
        "has", "have", "was", "were", "to", "for", "by", "this",
        "that", "with", "from", "are", "be", "it", "as", "or",
        "but", "not", "will", "can", "its", "also", "more", "than",
        "mr", "mrs", "dr", "said", "says"
    }
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    return [w for w in words if w not in stopwords and len(w) > 3]

def collect_rss_evidence(keywords: list) -> list:
    input_keywords = set(keywords[:6])
    evidences = []

    def fetch_feed(feed_url):
        try:
            feed = feedparser.parse(feed_url)
            results = []
            for entry in feed.entries[:10]:
                title    = entry.get("title", "")
                summary  = entry.get("summary", "")
                combined = (title + " " + summary)
                combined_lower = combined.lower()

                match_count = sum(1 for kw in input_keywords 
                                 if kw in combined_lower)
                if match_count >= 2:
                    results.append(combined[:300])
            return results
        except Exception:
            return []

    # All feeds parallel — no timeout killer
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_feed, url) for url in RSS_FEEDS]
        for future in as_completed(futures):
            try:
                results = future.result()
                evidences.extend(results)
            except Exception:
                continue

    return evidences[:5]

def collect_ddg_evidence(claim: str, keywords: list) -> list:
    query = " ".join(keywords[:4])
    evidences = []
    try:
        with DDGS() as ddgs:
            # Reduce to 3 results — faster!
            results = list(ddgs.text(query, max_results=3))
        for r in results:
            title = r.get("title", "")
            body  = r.get("body", "")
            combined = (title + " " + body)[:300]
            keyword_hits = sum(1 for kw in keywords[:5] 
                              if kw in combined.lower())
            if keyword_hits >= 2:
                evidences.append(combined)
    except Exception:
        pass
    return evidences

def collect_wiki_evidence(keywords: list) -> str:
    query = " ".join(keywords[:3])
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1
        }
        res = requests.get(search_url, params=params, timeout=5)
        results = res.json().get("query", {}).get("search", [])
        if not results:
            return ""

        title = results[0]["title"]
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
        summary_res = requests.get(summary_url, timeout=5)
        return summary_res.json().get("extract", "")[:500]
    except Exception:
        return ""

def collect_all_evidence(claim: str) -> dict:
    keywords = extract_keywords(claim)

    with ThreadPoolExecutor(max_workers=3) as executor:
            future_rss  = executor.submit(collect_rss_evidence, keywords)
            future_ddg  = executor.submit(collect_ddg_evidence, claim, keywords)
            future_wiki = executor.submit(collect_wiki_evidence, keywords)

            rss_evidence  = future_rss.result()
            ddg_evidence  = future_ddg.result()
            wiki_evidence = future_wiki.result()

    # Combine all into one evidence list
    all_evidence = rss_evidence + ddg_evidence
    if wiki_evidence:
        all_evidence.append(wiki_evidence)

    return {
        "evidences": all_evidence,
        "rss_count": len(rss_evidence),
        "ddg_count": len(ddg_evidence),
        "wiki_found": bool(wiki_evidence),
        "total": len(all_evidence)
    }