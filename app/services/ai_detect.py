import os
import httpx
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_URL = "https://router.huggingface.co/hf-inference/models/openai-community/roberta-base-openai-detector"

def detect_ai_text(text: str) -> dict:
    text = text[:500]

    if not HF_API_KEY or HF_API_KEY == "mock":
        return {
            "ai_probability": 0.15,
            "confidence": "low",
            "note": "Mock mode — HF API key not set"
        }

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": text}

    try:
        response = httpx.post(MODEL_URL, headers=headers, json=payload, timeout=20)

        if response.status_code != 200:
            return {
                "ai_probability": 0.0,
                "confidence": "low",
                "note": f"HTTP error {response.status_code}"
            }

        result = response.json()

        if isinstance(result, dict) and "error" in result:
            return {
                "ai_probability": 0.0,
                "confidence": "low",
                "note": "Model loading — try again in 20 seconds"
            }

        if isinstance(result, list) and len(result) > 0:
            scores = result[0]

            ai_score = next(
                (item["score"] for item in scores if item["label"].lower() == "fake"),
                0.0
            )

            return {
                "ai_probability": round(ai_score, 3),
                "confidence": "high" if ai_score > 0.7 else "medium" if ai_score > 0.4 else "low",
                "note": "Powered by RoBERTa AI detector"
            }

        return {
            "ai_probability": 0.0,
            "confidence": "low",
            "note": "Unexpected response format"
        }

    except httpx.TimeoutException:
        return {
            "ai_probability": 0.0,
            "confidence": "low",
            "note": "Request timed out"
        }

    except Exception as e:
        return {
            "ai_probability": 0.0,
            "confidence": "low",
            "note": f"API error: {str(e)}"
        }