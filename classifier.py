import os

# Securely pull AI settings from Azure Environment Variables
# Fizu or Zahra can plug these actual values into the Azure Portal configuration panel later!
AI_API_KEY = os.getenv("AI_API_KEY")
AI_ENDPOINT = os.getenv("AI_ENDPOINT")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "gpt-4o")

def classify_ticket(title, description):
    """
    Automatic ticket category suggestion function.
    Fizu (Person 4) will implement the actual Azure OpenAI / AI model client connection here.
    """
    if not AI_API_KEY or not AI_ENDPOINT:
        print("AI credentials missing in environment variables! Falling back to 'General' category.")
        return "General"
        
    try:
        # Fizu: Your AI API client logic and prompt schema will go here!
        # Example: response = client.chat.completions.create(...)
        
        # Simulated return value for testing purposes
        return "Technical Support"
    except Exception:
        return "General"
