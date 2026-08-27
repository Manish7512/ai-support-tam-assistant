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

    print("=" * 70)
    print("ACCOUNT HEALTH EVALUATION")
    print("=" * 70)

    for number, case in enumerate(TEST_CASES, start=1):

        account = accounts[case["account_index"]]

        print(
            f"\n[{number}/{total}] "
            f"{account['account_id']} - {account['company']}"
        )

        print("Expected status:", case["expected_status"])
        print("Actual account status:", account["health_status"])

        try:
            result = analyze_account_health(
                account,
                tickets,
            )

            summary = result.health_summary.lower()

            expected = case["expected_status"].lower()

            if expected in summary:
                correct += 1
                print("Result: PASS")
            else:
                print("Result: FAIL")

            print("\nHealth Summary:")
            print(result.health_summary)

            print("\nRisk Signals:")
            for signal in result.risk_signals:
                print("-", signal)

            print("\nRecommended Actions:")
            for action in result.recommended_actions:
                print("-", action)

        except Exception as e:
            print("ERROR:", type(e).__name__)
            print("Message:", str(e))

    accuracy = correct / total

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Health status accuracy: {accuracy:.2%}")
    print(f"Passed: {correct}/{total}")

    if accuracy >= 0.80:
        print("Evaluation: PASS")
    else:
        print("Evaluation: FAIL")


if __name__ == "__main__":
    evaluate()