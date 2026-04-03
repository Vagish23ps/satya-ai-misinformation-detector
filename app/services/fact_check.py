import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_KEY = os.getenv("GOOGLE_FACT_CHECK_KEY")

def normalize_verdict(rating: str) -> str:
    rating = rating.lower()
    if "false" in rating:
        return "FALSE"
    elif "misleading" in rating:
        return "MISLEADING"
    elif "true" in rating:
        return "TRUE"
    elif "unproven" in rating or "no evidence" in rating:
        return "UNVERIFIED"
    else:
        return "NO DATA FOUND"

def extract_keywords(text: str) -> list:
    stopwords = {
        "is", "the", "of", "and", "a", "an", "in", "on", "at",
        "has", "have", "was", "were", "to", "for", "by", "this",
        "that", "with", "from", "are", "be", "it", "as", "or"
    }
    words = text.lower().split()
    return [w for w in words if w not in stopwords and len(w) > 3]

def check_facts(text: str) -> dict:
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    # Send only first 100 chars as query — API works better with short queries
    short_query = text[:100]
    
    params = {
        "query": short_query,
        "key": GOOGLE_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "claims" not in data or len(data["claims"]) == 0:
            return {
                "verdict": "NO DATA FOUND",
                "claim": text,
                "source": None,
                "url": None
            }

        # Check top 3 claims for relevance
        input_keywords = set(extract_keywords(text))

        for claim in data["claims"][:3]:
            claim_text = claim.get("text", "").lower()
            claim_keywords = set(extract_keywords(claim_text))

            # Keyword overlap check
            overlap = input_keywords & claim_keywords
            overlap_ratio = len(overlap) / len(input_keywords) if input_keywords else 0

            if overlap_ratio >= 0.3:  # At least 30% keywords match
                review = claim["claimReview"][0]
                raw_rating = review.get("textualRating", "UNKNOWN")

                return {
                    "verdict": normalize_verdict(raw_rating),
                    "raw_rating": raw_rating,
                    "claim": claim.get("text", ""),
                    "source": review.get("publisher", {}).get("name", ""),
                    "url": review.get("url", ""),
                    "overlap_ratio": round(overlap_ratio, 2)
                }

        return {
            "verdict": "NO DATA FOUND",
            "claim": text,
            "source": None,
            "url": None
        }

    except Exception as e:
        return {
            "verdict": "ERROR",
            "error": str(e)
        }