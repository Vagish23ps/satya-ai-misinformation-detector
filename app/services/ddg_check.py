from duckduckgo_search import DDGS
import re

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

def check_ddg(text: str) -> dict:
    keywords = extract_keywords(text)

    if not keywords:
        return {
            "found": False,
            "verdict": "NO KEYWORDS",
            "note": "Could not extract keywords"
        }

    query = " ".join(keywords[:5])

    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(r)

        if not results:
            return {
                "found": False,
                "verdict": "NOT FOUND",
                "note": "No DDG results",
                "query_used": query
            }

        input_keywords = set(keywords)
        best_score = 0
        best_result = None

        for r in results:
            title = (r.get("title") or "").lower()
            body  = (r.get("body") or "").lower()
            combined = title + " " + body

            match_count = sum(1 for kw in input_keywords if kw in combined)
            match_ratio = match_count / len(input_keywords) if input_keywords else 0

            if match_ratio > best_score:
                best_score = match_ratio
                best_result = r

        if best_score >= 0.4:
            return {
                "found": True,
                "verdict": "FOUND ON WEB",
                "match_ratio": round(best_score, 2),
                "top_result": {
                    "title": best_result.get("title", ""),
                    "url": best_result.get("href", ""),
                    "snippet": best_result.get("body", "")[:200]
                },
                "query_used": query
            }
        else:
            return {
                "found": False,
                "verdict": "LOW RELEVANCE",
                "match_ratio": round(best_score, 2),
                "note": "Weak web presence",
                "query_used": query
            }

    except Exception as e:
        return {
            "found": False,
            "verdict": "ERROR",
            "note": str(e)
        }