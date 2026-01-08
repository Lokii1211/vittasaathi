def build_alert_message(txn, fraud_result):
    amount = txn["amount"]
    reasons = ", ".join(fraud_result["reasons"])

    if fraud_result["decision"] == "BLOCK":
        return (
            f"🚨 *Suspicious Transaction Blocked*\n\n"
            f"Amount: ₹{amount}\n"
            f"Reason: {reasons}\n\n"
            f"Reply YES if this was you.\n"
            f"Reply NO if this was NOT you."
        )

    if fraud_result["decision"] == "REVIEW":
        return (
            f"⚠️ *Transaction Needs Confirmation*\n\n"
            f"Amount: ₹{amount}\n"
            f"Reason: {reasons}\n\n"
            f"Reply YES or NO."
        )

    return None
