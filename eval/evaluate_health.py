import json
from pathlib import Path

from src.data_loader import load_accounts, load_tickets
from src.account_health import analyze_account_health


TEST_CASES = [
    {
        "account_index": 0,
        "expected_status": "At Risk",
    },
    {
        "account_index": 1,
        "expected_status": "Healthy",
    },
    {
        "account_index": 2,
        "expected_status": "New",
    },
    {
        "account_index": 25,
        "expected_status": "Churning",
    },
    {
        "account_index": 27,
        "expected_status": "Churning",
    },
]


def evaluate():
    accounts = load_accounts()
    tickets = load_tickets()

    total = len(TEST_CASES)
    correct = 0
    results = []

    print("=" * 70)
    print("ACCOUNT HEALTH EVALUATION")
    print("=" * 70)

    for number, case in enumerate(
        TEST_CASES,
        start=1,
    ):

        account = accounts[case["account_index"]]

        print(
            f"\n[{number}/{total}] "
            f"{account['account_id']} - "
            f"{account['company']}"
        )

        print(
            "Expected status:",
            case["expected_status"],
        )

        print(
            "Actual account status:",
            account["health_status"],
        )

        try:
            result = analyze_account_health(
                account,
                tickets,
            )

            summary = result.health_summary.lower()
            expected = case["expected_status"].lower()

            status_ok = expected in summary

            quality_score = 1.0 if status_ok else 0.0

            if status_ok:
                correct += 1
                print("Result: PASS")
            else:
                print("Result: FAIL")

            print(
                f"Quality score: {quality_score:.2f}"
            )

            print("\nHealth Summary:")
            print(result.health_summary)

            print("\nRisk Signals:")
            for signal in result.risk_signals:
                print("-", signal)

            print("\nRecommended Actions:")
            for action in result.recommended_actions:
                print("-", action)

            results.append(
                {
                    "account_id": account["account_id"],
                    "company": account["company"],
                    "expected_status": case[
                        "expected_status"
                    ],
                    "predicted_status": account[
                        "health_status"
                    ],
                    "passed": status_ok,
                    "quality_score": quality_score,
                }
            )

        except Exception as e:

            print("ERROR:", type(e).__name__)
            print("Message:", str(e))

            results.append(
                {
                    "account_id": account["account_id"],
                    "company": account["company"],
                    "expected_status": case[
                        "expected_status"
                    ],
                    "passed": False,
                    "quality_score": 0.0,
                    "error": str(e),
                }
            )

    accuracy = correct / total

    average_quality = sum(
        item["quality_score"]
        for item in results
    ) / len(results)

    report = {
        "task": "account_health",
        "test_cases": results,
        "summary": {
            "total_tests": total,
            "passed": correct,
            "health_status_accuracy": accuracy,
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
                existing["account_health"] = report
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
        f"Health status accuracy: {accuracy:.2%}"
    )
    print(
        f"Average quality score:  {average_quality:.2f}"
    )
    print(f"Passed: {correct}/{total}")

    if accuracy >= 0.80:
        print("Evaluation: PASS")
    else:
        print("Evaluation: FAIL")

    print(
        f"\nReport saved to: {report_path}"
    )


if __name__ == "__main__":
    evaluate()