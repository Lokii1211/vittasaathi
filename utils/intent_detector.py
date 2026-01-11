import re

def detect_intent(text: str):
    text_l = text.lower()

    amount_match = re.search(r"(\d+)", text_l)
    amount = int(amount_match.group(1)) if amount_match else None

    # CASH ENTRY (income or expense)
    if "cash" in text_l and amount:
        entry_type = "expense" if any(w in text_l for w in ["spent", "pay", "paid", "gave"]) else "income"
        return {
            "intent": "CASH_ENTRY",
            "amount": amount,
            "entry_type": entry_type
        }


    # 2️⃣ GREETING
    if any(w in text_l for w in ["hi", "hello", "hey"]):
        return {"intent": "GREETING", "amount": None}

    # 3️⃣ FRAUD
    if any(w in text_l for w in ["fraud", "scam", "scammed", "cheated"]):
        return {"intent": "FRAUD_QUERY", "amount": amount}

    # 4️⃣ LOAN
    if any(w in text_l for w in ["loan", "emi", "borrow"]):
        return {"intent": "LOAN_QUERY", "amount": amount}

    # 5️⃣ INVESTMENT
    if any(w in text_l for w in ["invest", "sip", "stocks", "mutual"]):
        return {"intent": "INVESTMENT_QUERY", "amount": amount}

    # 6️⃣ DASHBOARD
    if any(w in text_l for w in ["dashboard", "summary", "report", "monthly"]):
        return {"intent": "DASHBOARD_QUERY", "amount": None}

    # 7️⃣ INCOME / EXPENSE QUERIES
    if any(w in text_l for w in ["income", "earn", "salary", "made"]):
        return {"intent": "INCOME_QUERY", "amount": amount}

    if any(w in text_l for w in ["expense", "spent", "spend"]):
        return {"intent": "EXPENSE_QUERY", "amount": amount}

    return {"intent": "UNKNOWN", "amount": amount}

