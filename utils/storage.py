import csv
from pathlib import Path

FILE_PATH = Path("data/transactions.csv")

def save_transaction(txn: dict, user_id: str):
    with open(FILE_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            txn["amount"],
            txn["type"],
            txn["category"],
            txn["source"],
            txn["timestamp"],
            user_id
        ])

