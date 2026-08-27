from pydantic import BaseModel
from typing import Literal


class TriageOutput(BaseModel):
    product_area: Literal[
        "Authentication",
        "Data Ingestion",
        "Data Sources",
        "Dashboards",
        "Integrations",
        "Key Management",
        "Workflows",
        "Billing",
        "Onboarding",
    ]

    category: Literal[
        "Bug",
        "Feature Request",
        "How-To",
        "Performance",
        "Billing",
        "Integration",
        "Onboarding",
        "Data Loss",
    ]

    urgency: Literal["P1", "P2", "P3", "P4"]

    reasoning: str

    known_issue: bool

    kb_document: str | None = None

    kb_section: str | None = None

    responder_team: str

    first_response: str
    
class AccountHealthOutput(BaseModel):
    health_summary: str

    risk_signals: list[str]

    recommended_actions: list[str]
    
class TicketDraftOutput(BaseModel):
    draft_response: str