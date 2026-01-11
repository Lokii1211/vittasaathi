import csv
import statistics

TRANSACTION_FILE = "data/transactions.csv"

def is_amount_spike(user_id, amount):
    """
    Detects abnormal high amount compared to history
    """

    amounts = []

    with open(TRANSACTION_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["user_id"] == user_id and row["category"] == "EXPENSE":
                amounts.append(float(row["amount"]))

    if len(amounts) < 5:
        return False  # not enough history

    avg = statistics.mean(amounts)

    return amount > (avg * 3)

