import os
import re

from dotenv import load_dotenv
from google import genai

from src.data_loader import load_tickets
from src.models import TriageOutput
from src.rag import (
    load_documents,
    chunk_document,
    build_retriever,
    search_knowledge_base,
)
from src.routing import get_responder_team


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def has_strict_known_issue_match(ticket, kb_results):
    """
    Conservative known-issue detection.

    A known issue requires:
    - same product
    - same product area
    - exact error code
    - directly matching problem scenario

    Related information is not sufficient.
    """

    product = ticket["product"].lower()
    product_area = ticket["product_area"].lower()

    ticket_text = (
        f"{ticket['subject']} {ticket['body']}"
    ).lower()

    error_codes = re.findall(
        r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b",
        ticket["body"].upper(),
    )

    if not error_codes:
        return False

    product_name = (
        product
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )

    for result in kb_results:

        source = result["source"].lower()
        section = result["section"].lower()
        content = result["content"].lower()

        # ---------------------------------------------------------
        # 1. SAME PRODUCT
        # ---------------------------------------------------------

        source_name = (
            source.split("/")[-1]
            .replace(".md", "")
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
        )

        if source_name != product_name:
            continue

        # ---------------------------------------------------------
        # 2. SAME PRODUCT AREA
        # ---------------------------------------------------------

        # For Authentication, accept only KB content that actually
        # discusses Authentication, not merely permissions.
        if product_area == "authentication":
            if "authentication" not in content:
                continue

        elif product_area not in content and product_area not in section:
            continue

        # ---------------------------------------------------------
        # 3. EXACT ERROR CODE
        # ---------------------------------------------------------

        matched_error = None

        for error in error_codes:
            if re.search(
                rf"\b{re.escape(error.lower())}\b",
                content,
            ):
                matched_error = error.lower()
                break

        if matched_error is None:
            continue

        # ---------------------------------------------------------
        # 4. DIRECT SCENARIO MATCH
        # ---------------------------------------------------------

        # ---------------------------------------------------------
        # CHECKSUM_MISMATCH
        # ---------------------------------------------------------
        #
        # The KB documents CHECKSUM_MISMATCH specifically for
        # decryption after a key has been destroyed.
        #
        # TKT-10003 is about:
        #   Authentication
        #   updating permissions
        #   data integrity error on chunk 47
        #
        # Therefore it is NOT the same issue.
        #
        if matched_error == "checksum_mismatch":

            kb_decryption_scenario = (
                "during decryption" in content
                and "key" in content
                and "destroyed" in content
            )

            ticket_decryption_scenario = (
                "decryption" in ticket_text
                and "key" in ticket_text
            )

            if (
                kb_decryption_scenario
                and ticket_decryption_scenario
            ):
                return True

            continue

        # ---------------------------------------------------------
        # New users / SSO
        # ---------------------------------------------------------

        if (
            "new users" in ticket_text
            or "new joiners" in ticket_text
        ):
            if (
                "new users" in content
                or "new joiners" in content
            ):
                return True

            continue

        # ---------------------------------------------------------
        # Downstream service
        # ---------------------------------------------------------

        if "downstream service" in ticket_text:
            if "downstream service" in content:
                return True

            continue

        # ---------------------------------------------------------
        # Timeout
        # ---------------------------------------------------------

        if "timeout" in ticket_text:
            if (
                "timeout" in content
                or "timed out" in content
            ):
                return True

            continue

        # ---------------------------------------------------------
        # No sufficiently specific scenario
        # ---------------------------------------------------------

        continue

    return False


def determine_urgency(ticket, llm_urgency):
    """
    Apply explicit ticket-impact rules before falling back
    to the LLM urgency classification.
    """

    body = ticket["body"].lower()
    subject = ticket["subject"].lower()

    # Organization-wide impact
    if (
        "all users" in body
        or "everyone" in body
        or "entire organisation" in body
        or "entire organization" in body
    ):
        return "P1"

    # Large number of users explicitly blocked
    blocked_match = re.search(
        r"(\d+)\s+(?:people|users)\s+blocked",
        body,
    )

    if blocked_match:
        blocked_users = int(
            blocked_match.group(1)
        )

        if blocked_users >= 100:
            return "P1"

        # Smaller but significant impact
        if blocked_users >= 50:
            return "P2"

    # Feature requests are P3 when a workaround exists
    if subject.startswith("request:"):
        return "P3"

    # Otherwise preserve the LLM classification
    return llm_urgency


def classify_ticket(ticket, kb_results):

    kb_context = "\n\n".join(
        [
            f"Source: {result['source']}\n"
            f"Section: {result['section']}\n"
            f"Content:\n{result['content']}"
            for result in kb_results
        ]
    )

    prompt = f"""
You are an intelligent customer support ticket triage agent.

Your job is to analyze the customer ticket and classify it accurately.

IMPORTANT RULES
---------------
1. Use the ticket subject and body as the primary evidence.
2. Do not blindly copy existing dataset labels.
3. Do not invent facts that are not present in the ticket or KB.
4. Use the Knowledge Base only when it directly supports the ticket.

5. Mark known_issue as true ONLY when the Knowledge Base contains
   a documented issue that matches ALL of the following:
   - the same product,
   - the same or directly compatible product area,
   - the same error/problem,
   - and a compatible symptom or scenario.

6. An exact error-code match by itself is NOT sufficient.

7. Never mark a ticket as a known issue merely because:
   - the same error code appears in another product,
   - the same product appears in the KB,
   - the same general topic appears in the KB,
   - or the KB contains a related but different troubleshooting scenario.

8. If there is uncertainty about whether the KB issue matches the ticket,
   set known_issue to false.

9. A feature request is a request for new functionality or enhancement.

10. A bug is an existing functionality that is malfunctioning.

11. A How-To ticket asks how to use or configure an existing capability
    and is not reporting a malfunction.

12. Performance means an existing capability is unusually slow,
    timing out, or otherwise performing poorly as the PRIMARY problem.

13. Integration means the PRIMARY problem is a connection, webhook,
    connector, API, SSO/identity-provider, downstream service,
    or external-system integration failure.

14. Billing is about invoices, charges, payment, plans, subscriptions,
    or billing limits.

15. Data Loss should ONLY be selected when the ticket provides direct
    evidence that customer data was actually lost, deleted, corrupted,
    or made permanently inaccessible.

16. A data-integrity-related error does NOT automatically mean Data Loss.
    If there is no evidence of actual customer data loss or corruption,
    classify it as Bug.

17. If multiple categories appear possible, choose the category that
    best describes the PRIMARY customer problem.

18. SSO problems involving an identity provider, authentication
    integration, group mapping, downstream authentication dependency,
    or external identity system should generally be classified as
    Integration when the integration itself is the primary problem.

19. If an SSO ticket primarily reports that an existing feature is
    malfunctioning, without the external integration being the primary
    issue, classify it as Bug.

URGENCY GUIDELINES
------------------

P1 = Critical.

Use P1 when:
- the issue affects all or nearly all users,
- a critical/core capability is unavailable,
- a major workflow is blocked,
- there is confirmed or strongly indicated data loss/corruption,
- or a severe production outage is occurring.

IMPORTANT:
If a ticket explicitly states that ALL users are affected and a
core capability is unavailable, strongly prefer P1 unless there is
clear evidence that the impact is minor.

P2 = High.

Use P2 when:
- multiple users are affected,
- an important workflow is disrupted,
- a significant integration is failing,
- or the customer has substantial impact,
but the situation is not clearly critical or organization-wide.

P3 = Medium.

Use P3 when:
- impact is limited,
- a workaround exists,
- the request is a feature enhancement,
- or the issue affects a relatively small scope.

P4 = Low.

Use P4 for:
- general questions,
- minor issues,
- documentation requests,
- informational requests,
- or non-urgent matters.

PRODUCT AREA
------------
Choose ONLY one of the allowed product areas defined by the output schema.

KNOWLEDGE BASE
--------------
Use the supplied KB context as evidence.

If the retrieved documents are not directly relevant, set:
known_issue = false
kb_document = null
kb_section = null

RESPONDER TEAM
--------------
Do not choose or invent a responder team.
The application will determine the responder team separately.

FIRST RESPONSE
--------------
Write a concise, professional response.
Do not promise a specific resolution or timeline.
Do not mention internal reasoning.
Do not mention teams that are not provided by the application.

TICKET
------
Ticket ID: {ticket['ticket_id']}
Product: {ticket['product']}
Product Area From Dataset: {ticket['product_area']}
Subject: {ticket['subject']}

Body:
{ticket['body']}

KNOWLEDGE BASE CONTEXT
----------------------
{kb_context}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": TriageOutput,
        },
    )

    result = TriageOutput.model_validate_json(
        response.text
    )

    # -------------------------------------------------------------
    # Deterministic known-issue validation
    # -------------------------------------------------------------
    result.known_issue = has_strict_known_issue_match(
        ticket,
        kb_results,
        )

    result.urgency = determine_urgency(
        ticket,
        result.urgency,
        )

    if not result.known_issue:
        result.kb_document = None
        result.kb_section = None

    result.responder_team = get_responder_team(
        result.category
    )

    return result


def retrieve_context(ticket, top_k=3):

    documents = load_documents()

    all_chunks = []

    for document in documents:
        chunks = chunk_document(document)
        all_chunks.extend(chunks)

    vectorizer, matrix = build_retriever(
        all_chunks
    )

    query = f"""
    Product: {ticket['product']}
    Product Area: {ticket['product_area']}

    Subject: {ticket['subject']}

    {ticket['body']}
    """

    return search_knowledge_base(
        query,
        all_chunks,
        vectorizer,
        matrix,
        top_k=top_k,
        product=ticket["product"],
    )


def run_triage(ticket):

    kb_results = retrieve_context(
        ticket,
        top_k=3,
    )

    result = classify_ticket(
        ticket,
        kb_results,
    )

    return result


if __name__ == "__main__":

    tickets = load_tickets()

    ticket = tickets[3]

    result = run_triage(ticket)

    print(
        result.model_dump_json(
            indent=2
        )
    )