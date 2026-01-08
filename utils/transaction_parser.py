import re
from datetime import datetime

def parse_transaction_message(message: str):
    """
    Takes bank SMS / UPI message text
    Returns extracted transaction details
    """

    message_lower = message.lower()

    # 1️⃣ Detect amount
    amount_match = re.search(r"(rs\.?|₹)\s?([\d,]+)", message_lower)
    if not amount_match:
        return None  # Not a transaction

    amount = int(amount_match.group(2).replace(",", ""))

    # 2️⃣ Detect transaction type
    if "debit" in message_lower or "spent" in message_lower:
        txn_type = "debit"
    elif "credit" in message_lower or "received" in message_lower:
        txn_type = "credit"
    else:
        txn_type = "unknown"

    # 3️⃣ Detect source
    if "upi" in message_lower:
        source = "UPI"
    elif "card" in message_lower:
        source = "CARD"
    else:
        source = "BANK"

    return {
        "amount": amount,
        "type": txn_type,
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
