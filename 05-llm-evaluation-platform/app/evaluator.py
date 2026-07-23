"""Deterministic regression checks used by the web API and CI."""


def evaluate(case_id: str, answer: str) -> tuple[float, bool, list[str]]:
    """Score an answer without an API key; replace with an LLM judge in production."""
    normalized = answer.lower().strip()
    rules = {
        "password-reset": ["forgot", "reset", "email"],
        "refund-window": ["refund", "30"],
        "privacy-export": ["data", "settings", "30"],
    }
    required = rules.get(case_id, [])
    missing = [word for word in required if word not in normalized]
    unsafe = [word for word in ("guarantee", "ignore policy", "delete your account") if word in normalized]
    score = max(0.0, 1 - len(missing) / max(len(required), 1) - 0.5 * len(unsafe))
    reasons = ([f"Missing required idea: {word}" for word in missing] +
               [f"Potentially unsafe claim: {word}" for word in unsafe])
    return round(score, 2), score >= 0.8 and not unsafe, reasons or ["Passed deterministic policy checks."]
