from fastapi import FastAPI, HTTPException

from src.account_health import analyze_account_health
from src.data_loader import load_accounts, load_tickets
from src.ticket_draft import draft_response
from src.triage import run_triage


app = FastAPI(
    title="AI Support + TAM Assistant",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "AI Support + TAM Assistant API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/triage/{ticket_id}")
def triage_ticket(ticket_id: str):
    tickets = load_tickets()

    ticket = next(
        (
            ticket
            for ticket in tickets
            if ticket["ticket_id"] == ticket_id
        ),
        None,
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found",
        )

    result = run_triage(ticket)

    return result.model_dump()


@app.post("/draft-response/{ticket_id}")
def create_draft(ticket_id: str):
    tickets = load_tickets()

    ticket = next(
        (
            ticket
            for ticket in tickets
            if ticket["ticket_id"] == ticket_id
        ),
        None,
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found",
        )

    result = draft_response(ticket)

    return result.model_dump()


@app.post("/account-health/{account_id}")
def account_health(account_id: str):
    accounts = load_accounts()
    tickets = load_tickets()

    account = next(
        (
            account
            for account in accounts
            if account["account_id"] == account_id
        ),
        None,
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail=f"Account {account_id} not found",
        )

    result = analyze_account_health(
        account,
        tickets,
    )

    return result.model_dump()