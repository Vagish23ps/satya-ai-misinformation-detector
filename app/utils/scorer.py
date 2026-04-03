def calculate_truth_score(ai_result: dict, fact_result: dict, text: str = "",
                          wiki_result: str = "", news_result: dict = {},
                          semantic_result: dict = {}) -> dict:
    try:
        score = 100
        text_lower = text.lower()

        # --- WORD COUNT ---
        word_count = len(text.split())

        # --- 1. AI DETECTION ---
        ai_prob = float(ai_result.get("ai_probability", 0))
        if word_count < 15:
            ai_prob = ai_prob * 0.4
        score -= int(ai_prob * 30)

        # --- 2. GOOGLE FACT CHECK ---
        verdict_map = {
            "FALSE": 40, "MISLEADING": 35,
            "UNVERIFIED": 20, "TRUE": 0,
            "NO DATA FOUND": 8, "NO CLAIMS DETECTED": 3
        }
        fact_verdict = fact_result.get("verdict", "NO DATA FOUND").upper()
        score -= verdict_map.get(fact_verdict, 8)

        # --- 3. SEMANTIC EVIDENCE ---
        sem_verdict = semantic_result.get("verdict", "NO EVIDENCE")
        supports    = semantic_result.get("supports", 0)
        contradicts = semantic_result.get("contradicts", 0)
        neutral     = semantic_result.get("neutral", 0)
        confidence  = float(semantic_result.get("confidence", 0))

        if sem_verdict == "SUPPORTED":
            score += int(15 * confidence)
        elif sem_verdict == "WEAKLY SUPPORTED":
            score += 5
        elif sem_verdict == "CONTRADICTED":
            score -= int(35 * confidence)
        elif sem_verdict == "WEAKLY CONTRADICTED":
            score -= 15
        elif sem_verdict == "UNCERTAIN":
            score -= 5
        elif sem_verdict == "NO EVIDENCE":
            score -= 10

        # --- 4. EVIDENCE QUANTITY ---
        total_evidence = supports + contradicts + neutral
        neutral_ratio  = neutral / total_evidence if total_evidence > 0 else 0

        if total_evidence == 0:
            score -= 10
            no_evidence = True
        else:
            no_evidence = False

        if total_evidence >= 3:
            score += 5

        # --- 5. DANGER KEYWORDS (max -20) ---
        danger_keywords = [
            "5g", "microchip", "nanochip", "microchips",
            "secret", "secretly", "hiding", "hidden",
            "coverup", "cover-up", "suppressed", "censored",
            "they dont want", "leaked", "exposed",
            "hot water kills", "drinking hot water cures",
            "kills virus", "kills all virus",
            "home remedy", "guaranteed cure",
            "conspiracy", "hoax", "plandemic", "scamdemic",
            "deep state", "new world order", "mind control",
            "population control", "doctors hiding",
            "governments hiding", "scientists hiding",
            "free laptop", "free mobile", "free recharge",
            "government giving free", "apply now",
            "share before deleted", "forward this",
            "act now", "limited time", "no registration",
            "100 percent working", "guaranteed",
            "days of darkness", "6 days dark",
            "nasa confirms darkness", "earth will be dark",
            "solar storm blackout",
            "whatsapp forward", "share immediately"
        ]
        danger_hits = sum(1 for word in danger_keywords if word in text_lower)
        score -= min(danger_hits * 5, 20)

        # --- 6. ABSURD CLAIM DETECTION ---
        absurd_patterns = [
            "time loop", "repeating time", "world ended",
            "sky turned", "sky will turn", "permanently purple",
            "software glitch sky", "we are all dead",
            "earth stopped spinning", "sun disappeared",
            "gravity reversed", "humans can fly now",
            "teleportation discovered", "immortality achieved",
            "aliens took over", "simulation ended",
            "matrix confirmed", "flat earth proven",
            "moon is fake", "stars are holograms",
            "time travel confirmed", "parallel universe opened"
        ]
        absurd_hits = sum(1 for p in absurd_patterns if p in text_lower)

        if word_count < 10:
            score -= 20
        if absurd_hits > 0:
            score -= 40

        # --- CLAMP ---
        score = max(0, min(100, score))

        # --- RISK LEVEL ---
        if score >= 90:
            risk_level = "LOW RISK"
        elif score >= 70:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "HIGH RISK"

        # --- FINAL VERDICT (single block, priority order) ---
        if absurd_hits > 0:
            verdict = "LIKELY FALSE — Unrealistic or unverifiable claim"

        elif word_count < 10 and total_evidence == 0:
            verdict = "INSUFFICIENT DATA — Please provide more context"

        elif score >= 90:
            verdict = "LIKELY AUTHENTIC — High credibility content"

        elif fact_verdict in ["FALSE", "MISLEADING"]:
            verdict = "MISLEADING CONTENT — Do not share without verification"

        elif sem_verdict == "CONTRADICTED":
            verdict = "CONTRADICTED BY SOURCES — Likely false"

        elif sem_verdict == "WEAKLY CONTRADICTED":
            verdict = "DISPUTED — Sources partially contradict this claim"

        elif fact_verdict == "TRUE" or sem_verdict == "SUPPORTED" or \
             (neutral_ratio > 0.5 and ai_prob < 0.3 and score > 70):
            verdict = "LIKELY AUTHENTIC — Supported by multiple sources"

        elif sem_verdict == "WEAKLY SUPPORTED":
            verdict = "PARTIALLY VERIFIED — Limited source support"

        elif no_evidence:
            if ai_prob > 0.3:
                verdict = "SUSPICIOUS — AI-generated with no source verification"
            elif danger_hits > 0:
                verdict = "SUSPICIOUS CLAIM — Cannot be verified anywhere"
            else:
                verdict = "UNVERIFIABLE — No trace found in any news source"

        elif sem_verdict == "UNCERTAIN":
            if danger_hits > 0:
                verdict = "SUSPICIOUS — Unverifiable claim with risk signals"
            else:
                verdict = "UNCERTAIN — Mixed or insufficient evidence"

        else:
            verdict = "UNABLE TO DETERMINE — Please verify manually"

        return {
            "credibility_score": score,
            "risk_level": risk_level,
            "verdict": verdict,
            "ai_probability": ai_prob,
            "fact_verdict": fact_verdict,
            "semantic_verdict": sem_verdict,
            "evidence_count": total_evidence
        }

    except Exception as e:
        return {
            "credibility_score": 50,
            "risk_level": "UNKNOWN",
            "verdict": f"Scoring error: {str(e)}"
        }