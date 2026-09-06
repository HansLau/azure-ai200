from unittest.mock import patch
from classifier import suggest_category

test_cases = [
    ("Cannot access campus Wi-Fi", "I cannot connect to the campus Wi-Fi from my laptop.", "IT Support"),
    ("Aircon not working", "The aircon in room 302 has been broken for two days.", "Facilities"),
    ("Need to add a module", "I want to register for an additional course this semester.", "Course Registration"),
    ("Refund request", "I paid tuition twice by mistake and need a refund.", "Student Finance"),
    ("Overdue book fine", "I have a fine for a library book I returned late.", "Library Services"),
    ("General question", "What are your office hours?", "General Enquiry"),
]

def run_cases(label):
    print(f"\n--- {label} ---")
    passed = 0
    for title, desc, expected in test_cases:
        result = suggest_category(title, desc)
        status = "✅" if result["category"] == expected else "❌"
        if result["category"] == expected:
            passed += 1
        print(f"{status} Expected: {expected:25s} Got: {result['category']:25s} "
              f"(method: {result['method']}, confidence: {result['confidence']})")
    print(f"{passed}/{len(test_cases)} passed")


# 1. Normal run — AI should succeed and be used
run_cases("Normal run (AI available)")

# 2. Simulate AI completely failing (e.g. network error, bad key, quota exceeded)
with patch("classifier.classify_by_ai", side_effect=RuntimeError("Simulated AI outage")):
    run_cases("AI forced to fail (should fall back to keyword)")