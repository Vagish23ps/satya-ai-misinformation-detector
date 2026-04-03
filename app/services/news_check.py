import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def extract_keywords(text: str) -> list:
    stopwords = {
        "is", "the", "of", "and", "a", "an", "in", "on", "at",
        "has", "have", "was", "were", "to", "for", "by", "this",
        "that", "with", "from", "are", "be", "it", "as", "or",
        "but", "not", "we", "he", "she", "they", "his", "her",
        "will", "can", "been", "its", "also", "more", "than",
        "mr", "mrs", "dr", "said", "says", "according"
    }
    words = text.lower().split()
    return [w.strip(".,!?\"'") for w in words
            if w.strip(".,!?\"'") not in stopwords
            and len(w.strip(".,!?\"'")) > 3]


def check_news(text: str) -> dict:
    if not NEWS_API_KEY:
        return {
            "found": False,
            "verdict": "NO NEWS DATA",
            "note": "NewsAPI key not set"
        }

    keywords = extract_keywords(text)

    if not keywords:
        return {
            "found": False,
            "verdict": "NO KEYWORDS",
            "note": "Could not extract keywords"
        }

    # Use top 4 keywords for search
    query = " ".join(keywords[:4])

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 5  # Top 5 results only
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            return {
                "found": False,
                "verdict": "API ERROR",
                "note": data.get("message", "Unknown error")
            }

        articles = data.get("articles", [])

        if not articles:
            return {
                "found": False,
                "verdict": "NOT IN NEWS",
                "note": f"No news found for: {query}",
                "query_used": query
            }

        # Check keyword overlap with article titles/descriptions
        input_keywords = set(keywords)
        best_match = None
        best_score = 0

        for article in articles:
            title = (article.get("title") or "").lower()
            description = (article.get("description") or "").lower()
            combined = title + " " + description

            match_count = sum(1 for kw in input_keywords if kw in combined)
            match_ratio = match_count / len(input_keywords) if input_keywords else 0

            if match_ratio > best_score:
                best_score = match_ratio
                best_match = article

        if best_score >= 0.4:
            return {
                "found": True,
                "verdict": "FOUND IN NEWS",
                "match_ratio": round(best_score, 2),
                "top_article": {
                    "title": best_match.get("title", ""),
                    "source": best_match.get("source", {}).get("name", ""),
                    "url": best_match.get("url", ""),
                    "published": best_match.get("publishedAt", "")
                },
                "query_used": query
            }
        else:
            return {
                "found": False,
                "verdict": "LOW RELEVANCE",
                "note": "News found but not closely related",
                "query_used": query
            }

    except Exception as e:
        return {
            "found": False,
            "verdict": "ERROR",
            "note": str(e)
        }