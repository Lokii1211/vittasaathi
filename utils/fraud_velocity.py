import csv
from datetime import datetime, timedelta

TRANSACTION_FILE = "data/transactions.csv"

def count_recent_transactions(user_id, minutes=10):
    """
    Counts transactions in last N minutes
    """

    now = datetime.now()
    window_start = now - timedelta(minutes=minutes)

    count = 0

    with open(TRANSACTION_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["user_id"] != user_id:
                continue

            txn_time = datetime.fromisoformat(row["timestamp"])
            if txn_time >= window_start:
                count += 1

    return count

