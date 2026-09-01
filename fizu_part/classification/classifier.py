import logging
from keyword_classifier import classify_by_keyword
from ai_classifier import classify_by_ai

def suggest_category(title: str, description: str) -> dict:
    try:
        result = classify_by_ai(title, description)
        if result["confidence"] != "low":
            return result
    except Exception as e:
        logging.warning(f"AI classification failed, falling back to keyword: {e}")

    return classify_by_keyword(title, description)