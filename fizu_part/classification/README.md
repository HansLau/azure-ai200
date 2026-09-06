# Ticket Classification Module

This module suggests a **category** for a support ticket based on its title and description. It's designed to be called from the `POST /tickets` handler in the Azure Functions backend.

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

---

## Integration Guide (for whoever wires this into the Functions API)

Follow these steps to plug this module into the Azure Functions backend.

### Step 1: Copy the folder in

If the `backend/` folder doesn't have a `classification/` subfolder yet, copy this entire folder into it, so the structure looks like:

```
backend/
├── function_app.py              ← your Functions entry point
├── classification/
│   ├── keyword_classifier.py
│   ├── ai_classifier.py
│   ├── classifier.py
│   ├── test_keyword_classifier.py
│   ├── test_ai_classifier.py
│   ├── test_classifier.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── requirements.txt              ← main backend requirements
└── local.settings.json
```

### Step 2: Merge the dependencies

Open `classification/requirements.txt` and copy these two lines into the **main** `backend/requirements.txt` (don't just point to the subfolder's file — Azure Functions installs from the root one):

```
azure-ai-textanalytics==5.3.0
python-dotenv==1.0.1
```

Then reinstall dependencies in your Functions environment:
```bash
pip install -r requirements.txt
```

### Step 3: Set the environment variables

Locally, copy `classification/.env.example` to `classification/.env` and fill in real values (ask me for the actual key/endpoint — never share it over GitHub):

```
AZURE_LANGUAGE_ENDPOINT=your-endpoint-here
AZURE_LANGUAGE_KEY=your-key-here
```

**Important:** `.env` only works for local testing. Once deployed to Azure, add the same two variables to the **Function App's Configuration → Application settings** in the Azure Portal (or wire them through Key Vault if that's already set up). Without this step, the AI classifier will fail in production — though it'll safely fall back to keyword matching, it just won't use AI at all until this is done.

### Step 4: Call it from the ticket submission function

In your `POST /tickets` handler (likely in `function_app.py` or wherever that route is defined), import and call `suggest_category`:

```python
from classification.classifier import suggest_category

def create_ticket(req):
    data = req.get_json()
    title = data["title"]
    description = data["description"]

    classification_result = suggest_category(title, description)

    ticket = {
        "id": ...,                       # your existing ID generation
        "name": data["name"],
        "email": data["email"],
        "title": title,
        "description": description,
        "category": classification_result["category"],
        "classification_method": classification_result["method"],  # optional but recommended
        "priority": data.get("priority", "Medium"),
        "status": "New",
        "createdDate": ...                # your existing timestamp logic
    }

    # ... save `ticket` to Cosmos DB as you already do
```

The only two fields you need from the result are `classification_result["category"]` (required — this is the actual category) and `classification_result["method"]` (optional — nice for showing which logic path was used in the admin view).

### Step 5: Test the integration

1. Start the Functions app locally (`func start` or however your setup runs it).
2. Submit a test ticket through the frontend form, or with a tool like Postman/curl, using one of the example values below.
3. Confirm the ticket saved to Cosmos DB has the correct `category` field populated.

Example test payload:
```json
{
  "name": "Aiman Rahman",
  "email": "aiman@example.com",
  "title": "Cannot access campus Wi-Fi",
  "description": "I cannot connect to the campus Wi-Fi from my laptop."
}
```
Expected result: `category: "IT Support"`.

### Step 6: Confirm the fallback works in your environment too

Temporarily rename or blank out the `AZURE_LANGUAGE_KEY` value and submit a ticket again — it should still succeed and return a category, just with `method: "keyword"` instead of `"ai"`. This confirms the fallback chain survives real deployment conditions, not just local testing.

---

## Running the standalone tests

These don't require the Functions app running — they test the classification logic in isolation:

```bash
cd backend/classification
python test_keyword_classifier.py   # tests keyword-only logic
python test_ai_classifier.py        # tests AI-only logic (needs real .env values)
python test_classifier.py           # tests combined logic + simulated AI failure
```

## Known limitations

- Keyword matching is substring-based, so it can misfire on edge cases (e.g. a word that's a keyword for one category appearing in an unrelated context). The dictionary in `keyword_classifier.py` can be extended as more real ticket data comes in.
- AI classification depends on the Azure AI Language free tier being available and within quota. If it's down or the key is misconfigured, the system automatically falls back to keyword matching — no ticket submission ever fails because of this.
- Category list is currently fixed to the 6 categories in the project brief. Adding a new category means updating `CATEGORY_KEYWORDS` in `keyword_classifier.py`.

## Questions?


