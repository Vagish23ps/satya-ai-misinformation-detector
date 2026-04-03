from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_detect import detect_ai_text
from app.services.verifier import verify_claim
from app.utils.scorer import calculate_truth_score

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/analyze")
def analyze_text(input: TextInput):
    text = input.text

    if not text.strip():
        return {"error": "No text provided"}

    try:
        ai_result      = detect_ai_text(text)
        verified       = verify_claim(text)
        fact_result    = verified["fact_check"]
        semantic_result = verified.get("semantic", {})
        evidence_data  = verified.get("evidence", {})

        score_result = calculate_truth_score(
            ai_result=ai_result,
            fact_result=fact_result,
            text=text,
            semantic_result=semantic_result
        )

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

    return {
        "input_text": text[:100] + "..." if len(text) > 100 else text,
        "ai_detection": ai_result,
        "fact_check": fact_result,
        "evidence": evidence_data,
        "semantic": semantic_result,
        "truth_report": score_result
    }

@router.get("/test")
def test():
    return {"message": "SATYA Phase 2 running!"}

@router.post("/analyze")
def analyze_text(input: TextInput):
    text = input.text.strip()

    if not text:
        return {"error": "No text provided"}

    # --- SHORT INPUT CHECK ---
    word_count = len(text.split())
    if word_count < 6:
        return {
            "input_text": text,
            "ai_detection": {"ai_probability": 0, "confidence": "N/A", "note": "Input too short"},
            "fact_check": {"verdict": "NO DATA FOUND"},
            "evidence": {"total": 0},
            "semantic": {"verdict": "NO EVIDENCE", "supports": 0, "contradicts": 0, "neutral": 0, "details": []},
            "truth_report": {
                "credibility_score": 0,
                "risk_level": "HIGH RISK",
                "verdict": "INSUFFICIENT DATA — Please provide more context for accurate analysis",
                "ai_probability": 0,
                "fact_verdict": "NO DATA FOUND",
                "semantic_verdict": "NO EVIDENCE",
                "evidence_count": 0
            }
        }

    try:
        ai_result      = detect_ai_text(text)
        verified       = verify_claim(text)
        fact_result    = verified["fact_check"]
        wiki_result    = verified.get("wiki", "")
        semantic_result = verified.get("semantic", {})
        evidence_data  = verified.get("evidence", {})

        score_result = calculate_truth_score(
            ai_result=ai_result,
            fact_result=fact_result,
            text=text,
            wiki_result=wiki_result,
            semantic_result=semantic_result
        )

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

    return {
        "input_text": text[:100] + "..." if len(text) > 100 else text,
        "ai_detection": ai_result,
        "fact_check": fact_result,
        "evidence": evidence_data,
        "semantic": semantic_result,
        "truth_report": score_result
    }