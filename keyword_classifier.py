CATEGORY_KEYWORDS = {
    "IT Support": ["wifi", "wi-fi", "login", "password", "laptop", "network",
                   "printer", "vpn", "email", "computer", "software", "account locked"],
    "Facilities": ["aircon", "air conditioning", "lighting", "room", "building",
                   "cleaning", "maintenance", "key", "broken", "leak", "furniture"],
    "Course Registration": ["enrol", "enroll", "register", "add/drop", "timetable",
                             "class", "module", "course", "schedule", "credit"],
    "Student Finance": ["tuition", "fee", "payment", "refund", "scholarship",
                         "invoice", "billing", "loan", "financial aid"],
    "Library Services": ["book", "borrow", "library", "journal", "fine", "renew",
                          "overdue", "database access", "study room"],
}
DEFAULT_CATEGORY = "General Enquiry"

def classify_by_keyword(title: str, description: str) -> dict:
    text = f"{title} {description}".lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits > 0:
            scores[category] = hits

    if not scores:
        return {"category": DEFAULT_CATEGORY, "method": "keyword", "confidence": "low"}

    best_category = max(scores, key=scores.get)
    return {"category": best_category, "method": "keyword", "confidence": "medium"}