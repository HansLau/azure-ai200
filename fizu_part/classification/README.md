
# PROGRESS SO FAR!!!
   ONLY THE keyword_classifier.py IS WORKING!! 
   
   and the ai one still in progress because I don't the backend architecture we're going with so it like shot in the dark of testing. I did some local testing for AI and it working fine locally not for the project

   you can see the test_keyword_classifier.py for how to use the keyword_classifier.py

   you can test the code by running

```bash
   python test_keyword_classifier.py
```

BELOW is the more detailed explanation of my plan but still work in progress for integration with other part 😊👌


# Ticket Classification Module

This module suggests a **category** for a support ticket based on its title and description. It's designed to be dropped into the backend (Azure Functions) and called from the `POST /tickets` handler.

Location in repo: `backend/classification/`

## What it does

Given a ticket's `title` and `description`, it returns one of:

- `IT Support`
- `Facilities`
- `Course Registration`
- `Student Finance`
- `Library Services`
- `General Enquiry` (default/fallback when nothing matches)

## How it works

There are two classification methods, combined into one entry point:

| File | What it does |
|---|---|
| `keyword_classifier.py` | Matches ticket text against a hand-built dictionary of keywords per category. No external dependencies, always works, zero cost. |
| `ai_classifier.py` | Calls **Azure AI Language** (key phrase extraction) to pull out key phrases from the ticket text, then matches those phrases against the same keyword dictionary. Needs an Azure resource + API key. |
| `classifier.py` | The single function everyone should import. Tries the AI method first; if it fails (API error, timeout, low-confidence result) it automatically falls back to the keyword method. |

**Why both?** The keyword approach is a guaranteed-working baseline (good for reliability and the live demo). The AI approach adds smarter matching for phrasing the keyword list doesn't catch. Combining them means a flaky/slow API call during the demo never breaks ticket submission — it just silently falls back.

## The function you actually call

```python
from classification.classifier import suggest_category

result = suggest_category(title, description)
# {"category": "IT Support", "method": "ai", "confidence": "high"}
```

**Input:**
- `title` (str)
- `description` (str)

**Output:** a dict with:
- `category` — one of the 6 categories listed above
- `method` — `"ai"` or `"keyword"`, tells you which path was used
- `confidence` — `"high"`, `"medium"`, or `"low"`

Recommendation: store `method` alongside the ticket in Cosmos DB. It's a nice detail to show in the admin view / demo (e.g. a small tag showing whether AI or keyword logic classified it).

## Setup (for whoever integrates this)

1. Copy the `classification/` folder into `backend/`.
2. Merge the contents of `classification/requirements.txt` into the main backend `requirements.txt`:
   ```
   azure-ai-textanalytics==5.3.0
   python-dotenv==1.0.1
   ```
3. Add these environment variables (locally via `.env`, or in Azure via Function App settings / Key Vault):
   ```
   AZURE_LANGUAGE_ENDPOINT=<your Language resource endpoint>
   AZURE_LANGUAGE_KEY=<your Language resource key>
   ```
   These should ultimately be pulled from **Azure Key Vault** in production, not hardcoded.
4. In the ticket submission handler (`POST /tickets`), call:
   ```python
   from classification.classifier import suggest_category

   classification_result = suggest_category(ticket.title, ticket.description)
   ticket.category = classification_result["category"]
   ticket.classification_method = classification_result["method"]
   ```

## Testing

Each file has a matching test file with the same sample tickets, so you can compare how keyword-only vs. AI-only vs. combined logic classify the same inputs:

```bash
python test_keyword_classifier.py
python test_ai_classifier.py
python test_classifier.py
```

## Known limitations

- Keyword matching is substring-based, so it can misfire on edge cases (e.g. a word that's a keyword for one category appearing in an unrelated context). The dictionary in `keyword_classifier.py` can be extended as more real ticket data comes in.
- AI classification depends on the Azure AI Language free tier being available and within quota. If it's down or the key is misconfigured, the system automatically falls back to keyword matching — no ticket submission ever fails because of this.
- Category list is currently fixed to the 6 categories in the project brief. Adding a new category means updating `CATEGORY_KEYWORDS` in `keyword_classifier.py`.

## Questions?

Ping [your name] — this module owns everything under `backend/classification/`.
