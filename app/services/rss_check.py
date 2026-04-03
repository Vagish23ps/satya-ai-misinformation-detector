import feedparser
import re

# Top reliable RSS feeds
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


def check_rss(text: str) -> dict:
    keywords = extract_keywords(text)

    if not keywords:
        return {
            "found": False,
            "verdict": "NO KEYWORDS",
            "note": "Could not extract keywords"
        }

    input_keywords = set(keywords[:6])  # Top 6 keywords
    best_match = None
    best_score = 0

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:  # Check top 10 articles
                title = (entry.get("title") or "").lower()
                summary = (entry.get("summary") or "").lower()
                combined = title + " " + summary

                match_count = sum(1 for kw in input_keywords if kw in combined)
                match_ratio = match_count / len(input_keywords) if input_keywords else 0

                if match_ratio > best_score:
                    best_score = match_ratio
                    best_match = {
                        "title": entry.get("title", ""),
                        "source": feed_url.split("/")[2],
                        "url": entry.get("link", ""),
                        "published": entry.get("published", "")
                    }

        except Exception:
            continue  # Skip broken feeds silently

    if best_score >= 0.4:
        return {
            "found": True,
            "verdict": "FOUND IN NEWS",
            "match_ratio": round(best_score, 2),
            "top_article": best_match
        }
    elif best_score > 0:
        return {
            "found": False,
            "verdict": "LOW RELEVANCE",
            "match_ratio": round(best_score, 2),
            "note": "Weak news presence"
        }
    else:
        return {
            "found": False,
            "verdict": "NOT IN NEWS",
            "note": "No matching news found"
        }