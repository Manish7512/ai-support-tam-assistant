import json


def load_tickets():
    with open("data/tickets.json", "r") as file:
        tickets = json.load(file)

    return tickets


def load_accounts():
    with open("data/accounts.json", "r") as file:
        accounts = json.load(file)

    return accounts


if __name__ == "__main__":
    tickets = load_tickets()
    accounts = load_accounts()

    print("Number of tickets:", len(tickets))
    print("Number of accounts:", len(accounts))

    print("\nFirst ticket:")
    print(tickets[0])

    print("\nFirst account:")
    print(accounts[0])