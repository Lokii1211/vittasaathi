import csv
from collections import defaultdict
from datetime import datetime
import pandas as pd

TRANSACTION_FILE = "data/transactions.csv"

def build_daily_income_series(user_id):
    """
    Returns a DataFrame with:
    ds = date
    y  = daily income
    """

    daily_income = defaultdict(float)

    with open(TRANSACTION_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["user_id"] != user_id:
                continue

            if row["category"] != "INCOME":
                continue

            date = datetime.fromisoformat(row["timestamp"]).date()
            daily_income[date] += float(row["amount"])

    # Convert to DataFrame
    data = {
        "ds": list(daily_income.keys()),
        "y": list(daily_income.values())
    }

    df = pd.DataFrame(data)

    if df.empty:
        return None

    return df.sort_values("ds")

