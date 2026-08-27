import os

from dotenv import load_dotenv
from google import genai

from src.data_loader import load_tickets
from src.models import TicketDraftOutput
from src.triage import retrieve_context, classify_ticket


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def draft_response(ticket):
    # Retrieve relevant KB evidence
    kb_results = retrieve_context(ticket, top_k=3)

    # Get triage information
    triage_result = classify_ticket(ticket, kb_results)

    kb_context = "\n\n".join(
        [
            f"Source: {result['source']}\n"
            f"Section: {result['section']}\n"
            f"Content:\n{result['content']}"
            for result in kb_results
        ]
    )

    prompt = f"""
You are a customer support response drafting assistant.

Write a concise, professional response to the customer ticket.

TICKET
------
Product: {ticket['product']}
Subject: {ticket['subject']}

Body:
{ticket['body']}

TRIAGE RESULT
-------------
Category: {triage_result.category}
Urgency: {triage_result.urgency}
Known Issue: {triage_result.known_issue}

KNOWLEDGE BASE
--------------
{kb_context}

RULES
-----
1. Use the ticket as the primary source of truth.
2. Use the Knowledge Base only when it directly supports the response.
3. Do not invent troubleshooting steps.
4. Do not invent product capabilities.
5. Do not promise a specific resolution or timeline.
6. Do not mention internal reasoning.
7. Do not mention internal responder teams.
8. Do not expose internal KB scoring or retrieval details.
9. If the KB does not provide a supported resolution, acknowledge the
   issue and state that it is being reviewed.
10. Keep the response concise and professional.
11. Address the customer's actual problem directly.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": TicketDraftOutput,
        },
    )

    return TicketDraftOutput.model_validate_json(
        response.text
    )


if __name__ == "__main__":
    tickets = load_tickets()

    ticket = tickets[3]

    result = draft_response(ticket)

    print(result.model_dump_json(indent=2))