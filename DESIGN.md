# System Design

## 1. Overview

AI Support + TAM Assistant is a modular AI system for automating customer-support and Technical Account Management workflows.

Core capabilities:
- Ticket triage
- Knowledge-base retrieval
- Account health analysis
- Customer response drafting

FastAPI exposes these capabilities as REST endpoints.

## 2. High-Level Architecture

```text
                         Customer / Support Agent
                                   |
                                   v
                              FastAPI API
                                   |
              +--------------------+--------------------+
              |                    |                    |
              v                    v                    v
        Ticket Triage        Account Health      Response Drafting
              |                    |                    |
              v                    v                    v
          RAG / KB             Account Data          RAG / KB
              |                    |                    |
              +--------------------+--------------------+
                                   |
                                   v
                              Gemini LLM
                                   |
                                   v
                         Pydantic Validation
                                   |
                                   v
                            Structured Output
```

## 3. Ticket Triage

```text
Ticket
  ↓
Load Ticket Data
  ↓
Retrieve Relevant KB
  ↓
Build LLM Context
  ↓
Gemini
  ↓
TriageOutput
  ↓
Responder Routing
```

The model determines product area, category, urgency, reasoning, known issue, KB document/section, and first response.

Responder-team selection is handled separately by deterministic application logic.

## 4. RAG Design

The Knowledge Base consists of Markdown documents organized by product and troubleshooting topic.

```text
Markdown Files
      ↓
Document Loader
      ↓
Section Chunking
      ↓
TF-IDF Vectorization
      ↓
Cosine Similarity
      ↓
Product / Error-Code Boosting
      ↓
Top-K Results
      ↓
Gemini Context
```

Retrieval uses TF-IDF, unigrams/bigrams, cosine similarity, product-aware boosting, exact technical error-code matching, a minimum similarity threshold, and Top-K retrieval.

## 5. Known-Issue Detection

Known-issue detection is deliberately conservative.

A KB result should only be considered a known issue when it directly matches the ticket's:
- Product
- Product area
- Problem
- Error or scenario
- Symptoms

An error-code match by itself is not sufficient.

If the documentation is uncertain or unrelated:

```text
known_issue = false
kb_document = null
kb_section = null
```

## 6. Ticket Classification

```text
Feature Request → Request for new functionality
Bug             → Existing functionality is malfunctioning
How-To          → Asking how to use/configure an existing capability
Performance     → Slow, timing out, or poor-performing existing capability
Integration     → Connection, SSO, API, webhook, connector, downstream,
                  or external-system problem
Billing         → Invoice, payment, subscription, plan, or billing issue
Data Loss       → Actual lost, deleted, corrupted, or permanently inaccessible data
```

When multiple categories appear possible, the primary customer problem is used.

## 7. Urgency

```text
P1 → Critical
P2 → High
P3 → Medium
P4 → Low
```

Strong P1 signals include broad customer impact, major outage, actual data loss/corruption, or critical functionality being unavailable.

## 8. Account Health

```text
Account Data
     +
Customer Signals
     ↓
Gemini
     ↓
AccountHealthOutput
     ↓
Risk Signals + Recommended Actions
```

Relevant signals include ARR, plan, usage trend, seat utilization, login activity, open tickets, P1 history, NPS, renewal date, and escalation notes.

## 9. Response Drafting

```text
Ticket
  ↓
KB Retrieval
  ↓
Relevant Context
  ↓
Gemini
  ↓
Customer-Facing Draft
```

The drafting prompt requires grounded, concise responses and discourages invented troubleshooting, unsupported claims, internal reasoning, and unsupported resolution timelines.

## 10. Structured Outputs

```text
Gemini
  ↓
Structured JSON
  ↓
Pydantic Validation
  ↓
Application Output
```

Pydantic provides a predictable application-level contract for LLM responses.

## 11. Component Responsibilities

```text
src/data_loader.py
→ Loads tickets and account data

src/rag.py
→ Loads, chunks, indexes, and retrieves KB content

src/triage.py
→ Performs AI ticket classification

src/routing.py
→ Determines responder team

src/account_health.py
→ Generates account health analysis

src/ticket_draft.py
→ Generates customer response drafts

src/models.py
→ Defines Pydantic output schemas

src/api.py
→ Exposes REST API endpoints

eval/
→ Runs regression and quality evaluations
```

## 12. API Architecture

```text
Client
  ↓
FastAPI
  ↓
Application Logic
  ↓
Gemini / RAG / Data
  ↓
JSON Response
```

Endpoints:

```text
GET  /
GET  /health
POST /triage/{ticket_id}
POST /draft-response/{ticket_id}
POST /account-health/{account_id}
```

## 13. Evaluation Strategy

### Ticket Triage
Measures category, urgency, and known-issue accuracy.

Latest result:
```text
Category:      100%
Urgency:       100%
Known Issue:   100%
Overall:       100%
```

### Account Health
```text
Health Status: 100%
Passed: 5/5
```

### Response Drafting
```text
Passed: 5/5
Evaluation: PASS
```

## 14. Design Principles

### Grounded Generation
Use relevant internal knowledge as context rather than relying entirely on general model knowledge.

### Conservative Retrieval
Irrelevant KB results should not be treated as known issues.

### Deterministic Routing
Responder teams are selected by application logic rather than generated freely by the LLM.

### Structured Outputs
Pydantic validates model responses before they are returned.

### Evaluation-Driven Development
Evaluation scripts help detect regressions when prompts or application logic change.

## 15. Current Architecture Trade-offs

- **TF-IDF:** Lightweight, local, transparent, and easy to maintain.
- **Markdown KB:** Simple to update and version with Git.
- **Gemini:** Provides reasoning and generation with a simple integration.
- **Pydantic:** Provides a strong contract between the LLM and application.

## 16. Future Architecture

```text
                    API Gateway
                         |
                    Authentication
                         |
                    FastAPI Service
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Triage        Account Health   Drafting
          |              |              |
          +--------------+--------------+
                         |
                  Hybrid Retrieval
                         |
              +----------+----------+
              |                     |
              v                     v
        Vector Database        Metadata Store
              |
              v
           Gemini
              |
              v
       Structured Output
              |
              v
       Human Approval
              |
              v
        Customer Support
```

Potential production improvements:
- Embedding-based retrieval
- Vector database
- Hybrid search
- Metadata filtering
- Retrieval caching
- Authentication
- Rate limiting
- Observability
- Human approval workflows
- Automated grounding evaluation


