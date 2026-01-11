import csv
from collections import defaultdict
from datetime import datetime

TRANSACTION_FILE = "data/transactions.csv"

def get_monthly_income(user_id):
    """
    Returns dictionary:
    { '2025-01': 25000, '2025-02': 18000 }
    """

    monthly_income = defaultdict(float)

    with open(TRANSACTION_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["user_id"] != user_id:
                continue

            if row["category"] != "INCOME":
                continue

            timestamp = datetime.fromisoformat(row["timestamp"])
            month_key = timestamp.strftime("%Y-%m")

            monthly_income[month_key] += float(row["amount"])

    return dict(monthly_income)

