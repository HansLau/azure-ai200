import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from keyword_classifier import CATEGORY_KEYWORDS, DEFAULT_CATEGORY

load_dotenv()

def get_client():
    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

def classify_by_ai(title: str, description: str) -> dict:
    client = get_client()
    text = f"{title}. {description}"

    response = client.extract_key_phrases(documents=[text])[0]
    if response.is_error:
        raise RuntimeError(f"Language API error: {response.error}")

    phrases = [p.lower() for p in response.key_phrases]

    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for phrase in phrases for kw in keywords if kw in phrase)
        if hits > 0:
            scores[category] = hits

    if not scores:
        return {"category": DEFAULT_CATEGORY, "method": "ai", "confidence": "low"}

    best_category = max(scores, key=scores.get)
    return {"category": best_category, "method": "ai", "confidence": "high"}