import csv
import uuid
from datetime import datetime
from pathlib import Path

ALERT_FILE = Path("data/alerts.csv")

def create_alert(user_id, txn, fraud_result):
    alert_id = str(uuid.uuid4())

    with open(ALERT_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            alert_id,
            user_id,
            txn["amount"],
            fraud_result["decision"],
            "PENDING",
            "; ".join(fraud_result["reasons"]),
            datetime.now().isoformat()
        ])

    return alert_id

