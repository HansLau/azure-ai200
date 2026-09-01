from keyword_classifier import classify_by_keyword

test_cases = [
    ("Cannot access campus Wi-Fi", "I cannot connect to the campus Wi-Fi from my laptop.", "IT Support"),
    ("Aircon not working", "The aircon in room 302 has been broken for two days.", "Facilities"),
    ("Need to add a module", "I want to register for an additional course this semester.", "Course Registration"),
    ("Refund request", "I paid tuition twice by mistake and need a refund.", "Student Finance"),
    ("Overdue book fine", "I have a fine for a library book I returned late.", "Library Services"),
    ("General question", "What are your office hours?", "General Enquiry"),
]

passed = 0
for title, desc, expected in test_cases:
    result = classify_by_keyword(title, desc)
    status = "✅" if result["category"] == expected else "❌"
    if result["category"] == expected:
        passed += 1
    print(f"{status} Expected: {expected:25s} Got: {result['category']}")

print(f"\n{passed}/{len(test_cases)} passed")