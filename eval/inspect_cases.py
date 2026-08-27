from src.data_loader import load_tickets


tickets = load_tickets()

for index in [3, 4, 5]:

    ticket = tickets[index]

    print("=" * 70)
    print("TICKET:", ticket["ticket_id"])
    print("PRODUCT:", ticket["product"])
    print("PRODUCT AREA:", ticket["product_area"])
    print("CATEGORY LABEL IN DATA:", ticket["category"])
    print("URGENCY LABEL IN DATA:", ticket["urgency"])
    print("SUBJECT:", ticket["subject"])
    print()
    print(ticket["body"])
    print()