import os

from dotenv import load_dotenv
from google import genai

from src.data_loader import load_tickets
from src.models import AccountHealthOutput


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def get_account_context(account, tickets):
    account_id = account["account_id"]

    account_tickets = [
        ticket
        for ticket in tickets
        if ticket["account_id"] == account_id
    ]

    return {
        "account": account,
        "tickets": account_tickets,
    }


def analyze_account_health(account, tickets):
    context = get_account_context(account, tickets)

    account_data = context["account"]
    ticket_data = context["tickets"]

    prompt = f"""
You are a TAM (Technical Account Manager) assistant.

Analyze the customer account using ONLY the supplied account and
ticket information.

ACCOUNT
-------
{account_data}

TICKETS
-------
{ticket_data}

TASK
----
Produce a concise account health assessment.

HEALTH SUMMARY
--------------
Summarize the overall customer health using evidence from:
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
Do not invent risks that are not supported by the data.

RECOMMENDED ACTIONS
-------------------
Provide practical actions a TAM should take based on the identified
risks.

IMPORTANT
---------
- Use only the supplied data.
- Do not invent customer information.
- Do not assume missing NPS means positive or negative sentiment.
- If a field is None, treat it as unavailable.
- Prioritize concrete evidence over generic advice.
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