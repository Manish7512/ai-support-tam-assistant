# AI Support + TAM Assistant

An AI-powered Support & Technical Account Management assistant that automates **ticket triage, knowledge retrieval, account health analysis, and response drafting** using Gemini and RAG.

## 🚀 Features

### Ticket Triage

- Classifies product area and ticket category
- Assigns P1–P4 urgency
- Detects documented known issues
- Retrieves relevant Knowledge Base sections
- Routes tickets to the appropriate responder team
- Generates a concise first response

### RAG Knowledge Retrieval

- Local Markdown Knowledge Base
- Section-based chunking
- TF-IDF vectorization
- Cosine similarity search
- Product-aware retrieval
- Technical error-code matching and boosting

### Account Health

Analyzes:

- ARR and plan
- Usage trends
- Seat utilization
- Login activity
- Open/P1 tickets
- NPS
- Renewal information
- Escalation notes

Produces:

- Health summary
- Risk signals
- Recommended actions

### Response Drafting

Generates grounded customer-facing responses using the ticket and relevant KB context.

### REST API

FastAPI endpoints for:

- Ticket triage
- Response drafting
- Account health
- Health checks

---

## 🏗️ Architecture

```text
                         AI SUPPORT + TAM ASSISTANT
                                      |
                                  FastAPI
                                      |
              +-----------------------+-----------------------+
              |                       |                       |
              v                       v                       v
        Ticket Triage          Account Health        Response Drafting
              |                       |                       |
              v                       v                       v
          RAG / KB               Account Data             RAG / KB
              |                       |                       |
              +-----------+-----------+-----------+-----------+
                          |
                          v
                     Gemini LLM
                          |
                          v
                 Structured Outputs
                    (Pydantic)
```

### RAG Flow

```text
Markdown KB
    ↓
Document Loading
    ↓
Section Chunking
    ↓
TF-IDF
    ↓
Cosine Similarity
    ↓
Product / Error-Code Boosting
    ↓
Top-K Context
    ↓
Gemini
```

---

## 🛠️ Tech Stack

- **Python**
- **Google Gemini / google-genai**
- **Pydantic**
- **scikit-learn**
- **TF-IDF + Cosine Similarity**
- **FastAPI**
- **Uvicorn**
- **python-dotenv**
- **JSON / Markdown**

---

## 📁 Project Structure

```text
ai-support-tam-assistant/
├── data/
│   ├── accounts.json
│   └── tickets.json
├── knowledge-base/
│   ├── billing/
│   ├── onboarding/
│   ├── products/
│   └── troubleshooting/
├── src/
│   ├── account_health.py
│   ├── api.py
│   ├── data_loader.py
│   ├── models.py
│   ├── rag.py
│   ├── routing.py
│   ├── ticket_draft.py
│   └── triage.py
├── eval/
│   ├── evaluate.py
│   ├── evaluate_drafting.py
│   ├── evaluate_health.py
│   └── inspect_cases.py
├── .env.example
├── .gitignore
├── DESIGN.md
├── README.md
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Clone

```bash
git clone https://github.com/Manish7512/ai-support-tam-assistant.git
cd ai-support-tam-assistant
```

### 2. Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini

Create `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Never commit the real `.env` file.

---

## ▶️ Run

### Ticket Triage

```bash
python -m src.triage
```

### Account Health

```bash
python -m src.account_health
```

### Response Drafting

```bash
python -m src.ticket_draft
```

---

## 🌐 Run API

```bash
uvicorn src.api:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Example Requests

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl -X POST http://127.0.0.1:8000/triage/TKT-10000
```

```bash
curl -X POST http://127.0.0.1:8000/draft-response/TKT-10000
```

```bash
curl -X POST http://127.0.0.1:8000/account-health/ACC-3336
```

---

## 🧪 Evaluation

### Ticket Triage

```bash
python -m eval.evaluate
```

Latest result:

```text
Category accuracy:     100.00%
Urgency accuracy:      100.00%
Known-issue accuracy:  100.00%
Overall accuracy:      100.00%

Evaluation: PASS
```

### Account Health

```bash
python -m eval.evaluate_health
```

Latest result:

```text
Health status accuracy: 100.00%
Passed: 5/5

Evaluation: PASS
```

### Response Drafting

```bash
python -m eval.evaluate_drafting
```

Latest result:

```text
Drafting evaluation: 100.00%
Passed: 5/5

Evaluation: PASS
```

---

## 🔒 Grounding & Safety

The system is designed to:

- Use ticket content as primary evidence
- Use the Knowledge Base only when relevant
- Avoid unsupported claims
- Avoid invented troubleshooting steps
- Avoid false known-issue matches
- Distinguish Data Loss from data-integrity errors
- Treat SSO/external-system failures appropriately as Integration when applicable
- Keep responder routing deterministic
- Validate LLM output with Pydantic

---

## 📌 Current Status

| Component          | Status |
| ------------------ | ------ |
| Ticket Triage      | ✅     |
| RAG Retrieval      | ✅     |
| Gemini Integration | ✅     |
| Structured Output  | ✅     |
| Responder Routing  | ✅     |
| Account Health     | ✅     |
| Response Drafting  | ✅     |
| FastAPI            | ✅     |
| Evaluation         | ✅     |
| GitHub             | ✅     |

---

## 🔮 Future Improvements

- Embedding-based retrieval
- Vector database
- Hybrid search
- Retrieval caching
- Authentication and authorization
- API rate limiting
- Observability and tracing
- Human approval workflow
- Expanded automated grounding evaluation

---

## 🔗 Repository

https://github.com/Manish7512/ai-support-tam-assistant
