from src.data_loader import load_tickets
from src.ticket_draft import draft_response


TEST_CASES = [
    {
        "ticket_index": 0,
        "description": "Feature request",
    },
    {
        "ticket_index": 1,
        "description": "Feature request",
    },
    {
        "ticket_index": 3,
        "description": "Severe bug",
    },
    {
        "ticket_index": 4,
        "description": "Integration issue",
    },
    {
        "ticket_index": 5,
        "description": "Adversarial SSO case",
        "adversarial": True,
    },
]


def evaluate():
    tickets = load_tickets()

    print("=" * 70)
    print("TICKET RESPONSE DRAFTING EVALUATION")
    print("=" * 70)

    total = len(TEST_CASES)
    passed = 0

    for number, case in enumerate(TEST_CASES, start=1):

        ticket = tickets[case["ticket_index"]]

        print(
            f"\n[{number}/{total}] "
            f"Processing {ticket['ticket_id']}..."
        )

        print("Subject:", ticket["subject"])

        try:
            result = draft_response(ticket)

            draft = result.draft_response

            # Basic safety / grounding checks
            forbidden_terms = [
                "internal reasoning",
                "retrieval score",
                "similarity score",
                "kb score",
            ]

            has_forbidden_content = any(
                term in draft.lower()
                for term in forbidden_terms
            )

            if not has_forbidden_content and len(draft.strip()) > 20:
                passed += 1
                print("Result: PASS")
            else:
                print("Result: FAIL")

            print("\nDraft:")
            print(draft)

            if case.get("adversarial"):
                print("Adversarial case: YES")

        except Exception as e:
            print("Result: ERROR")
            print(type(e).__name__, str(e))

    accuracy = passed / total

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Drafting evaluation: {accuracy:.2%}")
    print(f"Passed: {passed}/{total}")

    if accuracy >= 0.80:
        print("Evaluation: PASS")
    else:
        print("Evaluation: FAIL")


if __name__ == "__main__":
    evaluate()