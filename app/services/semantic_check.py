from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load model once at startup — not on every request
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    return model.encode(text, convert_to_tensor=True)

def classify_stance(similarity: float) -> str:
    if similarity >= 0.60:
        return "SUPPORTS"
    elif similarity >= 0.35:
        return "NEUTRAL"
    else:
        return "IRRELEVANT"  # Below 35% = ignore completely

def semantic_verify(claim: str, evidences: list) -> dict:
    """
    evidences: list of strings (article titles + snippets)
    Returns aggregated stance verdict
    """
    if not evidences:
        return {
            "verdict": "NO EVIDENCE",
            "confidence": 0.0,
            "supports": 0,
            "contradicts": 0,
            "neutral": 0,
            "details": []
        }

    claim_embedding = get_embedding(claim)
    details = []
    supports = 0
    contradicts = 0
    neutral = 0

    for evidence in evidences[:5]:
        if not evidence or len(evidence.strip()) < 20:
            continue

        evidence_embedding = get_embedding(evidence)
        similarity = float(util.cos_sim(claim_embedding, evidence_embedding)[0][0])
        stance = classify_stance(similarity)

        if stance == "IRRELEVANT":
            continue  # Skip garbage evidence completely

        if stance == "SUPPORTS":
            supports += 1
        elif stance == "CONTRADICTS":
            contradicts += 1
        else:
            neutral += 1

        details.append({
            "snippet": evidence[:150],
            "similarity": round(similarity, 3),
            "stance": stance
        })

    total = supports + contradicts + neutral
    confidence = round(max(supports, contradicts) / total, 2) if total > 0 else 0.0

    # Final verdict based on majority
    if supports > contradicts and supports >= 2:
        verdict = "SUPPORTED"
    elif contradicts > supports and contradicts >= 2:
        verdict = "CONTRADICTED"
    elif supports > 0 and contradicts == 0:
        verdict = "WEAKLY SUPPORTED"
    elif contradicts > 0 and supports == 0:
        verdict = "WEAKLY CONTRADICTED"
    else:
        verdict = "UNCERTAIN"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "supports": supports,
        "contradicts": contradicts,
        "neutral": neutral,
        "details": details
    }