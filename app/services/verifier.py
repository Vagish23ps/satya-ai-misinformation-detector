from concurrent.futures import ThreadPoolExecutor
from app.services.fact_check import check_facts
from app.services.evidence_collector import collect_all_evidence
from app.services.semantic_check import semantic_verify

def verify_claim(text: str) -> dict:

    # Run fact_check and evidence PARALLEL — no timeout
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_fact     = executor.submit(check_facts, text)
        future_evidence = executor.submit(collect_all_evidence, text)

        fact_result   = future_fact.result()
        evidence_data = future_evidence.result()

    evidences = evidence_data.get("evidences", [])
    semantic_result = semantic_verify(text, evidences)

    return {
        "fact_check": fact_result,
        "evidence": evidence_data,
        "semantic": semantic_result
    }