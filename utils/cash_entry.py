from datetime import datetime

# Temporary in-memory DB (we’ll upgrade later)
CASH_DB = []

def save_cash_entry(user_id: str, amount: int, entry_type: str = "income"):
    record = {
        "user_id": user_id,
        "amount": amount,
        "type": entry_type,  # income / expense
        "source": "CASH",
        "timestamp": datetime.utcnow().isoformat()
    }
    CASH_DB.append(record)
    return record


def calculate_monthly_estimate(user_id: str):
    user_records = [r for r in CASH_DB if r["user_id"] == user_id]

    total = sum(r["amount"] for r in user_records if r["type"] == "income")

    # Simple estimate: avg daily × 30
    days = max(1, len(set(r["timestamp"][:10] for r in user_records)))
    daily_avg = total / days
    monthly_estimate = int(daily_avg * 30)

    return monthly_estimate

def calculate_monthly_expense(user_id: str):
    user_records = [r for r in CASH_DB if r["user_id"] == user_id and r["type"] == "expense"]
    return sum(r["amount"] for r in user_records)

