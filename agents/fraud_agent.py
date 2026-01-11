"""
Basic Fraud Detection Agent
Rule-based fraud detection for transactions
"""

def check_fraud(transaction: dict) -> dict:
    """
    Rule-based fraud detection
    Returns risk score and decision
    """
    
    risk_score = 0.0
    reasons = []
    
    amount = transaction.get("amount", 0)
    txn_type = transaction.get("type", "")
    category = transaction.get("category", "")
    
    # Rule 1: High amount threshold based on context
    if amount >= 10000:
        risk_score += 0.5
        reasons.append("Very high transaction amount (₹10,000+)")
    elif amount >= 5000:
        risk_score += 0.3
        reasons.append("High transaction amount (₹5,000+)")
    elif amount >= 3000:
        risk_score += 0.1
        reasons.append("Moderately high amount")
    
    # Rule 2: Debit/expense transactions are riskier
    if txn_type in ["debit", "expense"]:
        risk_score += 0.2
        reasons.append("Debit transaction")
    
    # Rule 3: Round amounts are suspicious (common in scams)
    if amount > 1000 and amount % 1000 == 0:
        risk_score += 0.15
        reasons.append("Round amount (common in fraud)")
    
    # Rule 4: Unusual categories
    suspicious_categories = ["transfer", "unknown", "other_expense"]
    if category.lower() in suspicious_categories:
        risk_score += 0.1
        reasons.append("Unusual category")
    
    # Decision logic
    if risk_score >= 0.8:
        decision = "BLOCK"
    elif risk_score >= 0.5:
        decision = "REVIEW"
    else:
        decision = "ALLOW"
    
    return {
        "risk_score": round(risk_score, 2),
        "decision": decision,
        "reasons": reasons
    }

