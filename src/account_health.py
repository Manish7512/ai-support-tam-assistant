import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from google import genai

from src.data_loader import load_tickets
from src.models import AccountHealthOutput


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def get_account_context(account, tickets, days=90):
    account_id = account["account_id"]

    account_tickets = [
        ticket
        for ticket in tickets
        if ticket["account_id"] == account_id
    ]

    # Keep only tickets from the last 90 days
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    recent_tickets = []

    for ticket in account_tickets:
        created_at = ticket.get("created_at")

        if not created_at:
            continue

        try:
            ticket_date = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )

            if ticket_date >= cutoff:
                recent_tickets.append(ticket)

        except ValueError:
            # Ignore tickets with invalid dates
            continue

    return {
        "account": account,
        "tickets": recent_tickets,
    }


def analyze_account_health(account, tickets):
    context = get_account_context(
        account,
        tickets,
        days=90,
    )

    account_data = context["account"]
    ticket_data = context["tickets"]

    prompt = f"""
You are a TAM (Technical Account Manager) assistant.

Analyze the customer account using ONLY the supplied account and
ticket information.

ACCOUNT
-------
{account_data}

TICKETS FROM THE LAST 90 DAYS
-----------------------------
{ticket_data}

TASK
----
Produce a concise account health assessment.

HEALTH SUMMARY
--------------
Write an executive-level summary in 3 to 5 sentences.

The summary should consider:
- health status
- usage trend
- open tickets
- P1 ticket history
- NPS
- renewal date
- ARR
- active versus licensed seats
- escalation notes
- recent ticket patterns

RISK SIGNALS
------------
List the most important concrete risks.

For every risk involving:
- churn
- escalation
- customer frustration
- competing vendors
- repeated severe incidents

include a short DIRECT QUOTE from the relevant ticket or
escalation information when such a quote exists.

Do not invent quotes.

Only report risks supported by the supplied data.

RECOMMENDED ACTIONS
-------------------
Provide practical TAM talking points/actions based on the identified
risks.

Actions should be specific to this customer rather than generic advice.

IMPORTANT
---------
- Use only the supplied account and ticket data.
- Only use tickets from the supplied last-90-day context.
- Do not invent customer information.
- Do not invent ticket details.
- Do not invent quotes.
- Do not assume missing NPS means positive or negative sentiment.
- If a field is None, treat it as unavailable.
- Prioritize concrete evidence over generic advice.
- Do not blindly follow existing dataset labels.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": AccountHealthOutput,
        },
    )

    return AccountHealthOutput.model_validate_json(
        response.text
    )


if __name__ == "__main__":
    from src.data_loader import load_accounts

    accounts = load_accounts()
    tickets = load_tickets()

    account = accounts[0]

    result = analyze_account_health(
        account,
        tickets,
    )

    print(result.model_dump_json(indent=2))