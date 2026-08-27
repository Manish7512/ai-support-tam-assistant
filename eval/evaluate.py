import json
from pathlib import Path

from src.data_loader import load_tickets
from src.triage import run_triage


TEST_CASES = [
    {
        "ticket_index": 0,
        "expected_category": "Feature Request",
        "expected_urgency": "P3",
        "expected_known_issue": False,
    },
    {
        "ticket_index": 1,
        "expected_category": "Feature Request",
        "expected_urgency": "P3",
        "expected_known_issue": False,
    },
    {
        "ticket_index": 3,
        "expected_category": "Bug",
        "expected_urgency": "P1",
        "expected_known_issue": False,
    },
    {
        "ticket_index": 4,
        "expected_category": "Integration",
        "expected_urgency": "P1",
        "expected_known_issue": False,
    },
    {
        "ticket_index": 5,
        "expected_category": "Integration",
        "expected_urgency": "P2",
        "expected_known_issue": False,
        "adversarial": True,
    },
]


def evaluate():
    tickets = load_tickets()

    total = len(TEST_CASES)
    results = []

    category_correct = 0
    urgency_correct = 0
    known_issue_correct = 0

    print("=" * 70)
    print("TICKET TRIAGE EVALUATION")
    print("=" * 70)

    for case_number, case in enumerate(TEST_CASES, start=1):

        ticket = tickets[case["ticket_index"]]

        print(
            f"\n[{case_number}/{total}] "
            f"Processing {ticket['ticket_id']}..."
        )
        print("Subject:", ticket["subject"])

        try:
            result = run_triage(ticket)

            category_ok = (
                result.category == case["expected_category"]
            )

            urgency_ok = (
                result.urgency == case["expected_urgency"]
            )

            known_issue_ok = (
                result.known_issue
                == case["expected_known_issue"]
            )

            if category_ok:
                category_correct += 1

            if urgency_ok:
                urgency_correct += 1

            if known_issue_ok:
                known_issue_correct += 1

            passed_checks = sum(
                [
                    category_ok,
                    urgency_ok,
                    known_issue_ok,
                ]
            )

            quality_score = passed_checks / 3
            passed = quality_score == 1.0

            print(
                "Category:",
                result.category,
                "| Expected:",
                case["expected_category"],
                "|",
                "PASS" if category_ok else "FAIL",
            )

            print(
                "Urgency:",
                result.urgency,
                "| Expected:",
                case["expected_urgency"],
                "|",
                "PASS" if urgency_ok else "FAIL",
            )

            print(
                "Known issue:",
                result.known_issue,
                "| Expected:",
                case["expected_known_issue"],
                "|",
                "PASS" if known_issue_ok else "FAIL",
            )

            print(
                f"Quality score: {quality_score:.2f}"
            )

            if case.get("adversarial"):
                print("Adversarial case: YES")

            results.append(
                {
                    "ticket_id": ticket["ticket_id"],
                    "subject": ticket["subject"],
                    "expected_category": case["expected_category"],
                    "predicted_category": result.category,
                    "expected_urgency": case["expected_urgency"],
                    "predicted_urgency": result.urgency,
                    "expected_known_issue": case[
                        "expected_known_issue"
                    ],
                    "predicted_known_issue": result.known_issue,
                    "category_pass": category_ok,
                    "urgency_pass": urgency_ok,
                    "known_issue_pass": known_issue_ok,
                    "passed": passed,
                    "quality_score": quality_score,
                    "adversarial": case.get(
                        "adversarial",
                        False,
                    ),
                }
            )

        except Exception as e:

            print("ERROR:", type(e).__name__)
            print("Message:", str(e))

            results.append(
                {
                    "ticket_id": ticket["ticket_id"],
                    "subject": ticket["subject"],
                    "passed": False,
                    "quality_score": 0.0,
                    "error": str(e),
                    "adversarial": case.get(
                        "adversarial",
                        False,
                    ),
                }
            )

    category_accuracy = category_correct / total
    urgency_accuracy = urgency_correct / total
    known_issue_accuracy = known_issue_correct / total

    overall_accuracy = (
        category_accuracy
        + urgency_accuracy
        + known_issue_accuracy
    ) / 3

    average_quality = sum(
        item["quality_score"]
        for item in results
    ) / len(results)

    report = {
        "task": "ticket_triage",
        "test_cases": results,
        "summary": {
            "total_tests": total,
            "passed": sum(
                item["passed"]
                for item in results
            ),
            "category_accuracy": category_accuracy,
            "urgency_accuracy": urgency_accuracy,
            "known_issue_accuracy": known_issue_accuracy,
            "overall_accuracy": overall_accuracy,
            "average_quality_score": average_quality,
        },
    }

    report_path = Path("eval/eval_report.json")

    if report_path.exists():
        try:
            existing = json.loads(
                report_path.read_text(
                    encoding="utf-8"
                )
            )

            if isinstance(existing, dict):
                existing["ticket_triage"] = report
                report = existing

        except json.JSONDecodeError:
            pass

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Category accuracy:     {category_accuracy:.2%}"
    )
    print(
        f"Urgency accuracy:      {urgency_accuracy:.2%}"
    )
    print(
        f"Known-issue accuracy:  {known_issue_accuracy:.2%}"
    )
    print(
        f"Overall accuracy:      {overall_accuracy:.2%}"
    )
    print(
        f"Average quality score: {average_quality:.2f}"
    )

    if overall_accuracy >= 0.80:
        print("Evaluation: PASS")
    else:
        print("Evaluation: FAIL")

    print(
        f"\nReport saved to: {report_path}"
    )


if __name__ == "__main__":
    evaluate()