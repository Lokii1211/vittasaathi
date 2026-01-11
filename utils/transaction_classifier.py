def classify_transaction(transaction: dict, original_message: str):
    """
    Classifies transaction into INCOME / EXPENSE / TRANSFER
    """

    msg = original_message.lower()
    txn_type = transaction["type"]

    # Keywords for income
    income_keywords = [
        "salary", "credited", "received", "payment from",
        "payout", "settlement", "reward"
    ]

    # Keywords for transfers
    transfer_keywords = [
        "self", "own account", "to bank", "withdrawal"
    ]

    # CREDIT logic
    if txn_type == "credit":
        for word in income_keywords:
            if word in msg:
                return "INCOME"
        return "INCOME"  # default credit → income

    # DEBIT logic
    if txn_type == "debit":
        for word in transfer_keywords:
            if word in msg:
                return "TRANSFER"
        return "EXPENSE"

    return "UNKNOWN"

