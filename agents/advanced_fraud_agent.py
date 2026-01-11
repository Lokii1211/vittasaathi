"""
Advanced Fraud Detection Agent
Behavioral and pattern-based fraud detection
"""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from database.transaction_repository import transaction_repo


def advanced_fraud_check(user_id: str, txn: dict) -> dict:
    """
    Advanced fraud detection using behavioral patterns
    """
    
    risk_score = 0.0
    reasons = []
    
    amount = txn.get("amount", 0)
    source = txn.get("source", "UNKNOWN")
    
    # Check 1: Transaction velocity (too many in short time)
    recent_count = transaction_repo.count_recent_transactions(user_id, minutes=10)
    if recent_count >= 5:
        risk_score += 0.5
        reasons.append(f"High velocity: {recent_count} transactions in 10 minutes")
    elif recent_count >= 3:
        risk_score += 0.2
        reasons.append(f"Multiple transactions: {recent_count} in 10 minutes")
    
    # Check 2: New payee detection
    if transaction_repo.is_new_payee(user_id, source) and source != "MANUAL":
        risk_score += 0.3
        reasons.append(f"New payee/source: {source}")
    
    # Check 3: Amount spike (compared to historical average)
    is_spike, spike_ratio = check_amount_spike(user_id, amount)
    if is_spike:
        risk_score += 0.4
        reasons.append(f"Amount spike: {spike_ratio:.1f}x higher than average")
    
    # Check 4: Time-based patterns (unusual hours)
    from datetime import datetime
    hour = datetime.now().hour
    if hour >= 23 or hour <= 5:
        risk_score += 0.2
        reasons.append("Transaction at unusual hour (11PM - 5AM)")
    
    # Check 5: Duplicate transaction detection
    is_duplicate = check_duplicate_transaction(user_id, amount)
    if is_duplicate:
        risk_score += 0.3
        reasons.append("Possible duplicate transaction")
    
    # Decision
    if risk_score >= 0.7:
        decision = "BLOCK"
    elif risk_score >= 0.4:
        decision = "REVIEW"
    else:
        decision = "ALLOW"
    
    return {
        "risk_score": round(risk_score, 2),
        "decision": decision,
        "reasons": reasons
    }


def check_amount_spike(user_id: str, amount: int) -> tuple:
    """Check if amount is abnormally high compared to history"""
    
    # Get user's average transaction
    avg_expense = transaction_repo.get_average_daily_expense(user_id, days=30)
    
    if avg_expense <= 0:
        return False, 1.0
    
    ratio = amount / avg_expense
    
    # If 3x higher than daily average, it's a spike
    if ratio >= 3:
        return True, ratio
    
    return False, ratio


def check_duplicate_transaction(user_id: str, amount: int) -> bool:
    """Check for duplicate transactions in last 5 minutes"""
    
    from datetime import datetime, timedelta
    
    recent = transaction_repo.get_user_transactions(
        user_id,
        start_date=datetime.now() - timedelta(minutes=5),
        limit=10
    )
    
    # Count same-amount transactions
    same_amount_count = sum(1 for t in recent if t.get("amount") == amount)
    
    return same_amount_count >= 2


def comprehensive_fraud_analysis(user_id: str, txn: dict) -> dict:
    """
    Complete fraud analysis combining all checks
    Returns detailed analysis with recommendations
    """
    
    from agents.fraud_agent import check_fraud
    
    # Run both basic and advanced checks
    basic = check_fraud(txn)
    advanced = advanced_fraud_check(user_id, txn)
    
    # Combine scores
    combined_score = (basic["risk_score"] + advanced["risk_score"]) / 2
    all_reasons = basic["reasons"] + advanced["reasons"]
    
    # Final decision
    if combined_score >= 0.7 or "BLOCK" in [basic["decision"], advanced["decision"]]:
        decision = "BLOCK"
        action = "Transaction blocked. User must confirm via YES/NO."
    elif combined_score >= 0.4 or "REVIEW" in [basic["decision"], advanced["decision"]]:
        decision = "REVIEW"
        action = "Transaction flagged for review. Awaiting user confirmation."
    else:
        decision = "ALLOW"
        action = "Transaction approved."
    
    return {
        "decision": decision,
        "combined_risk_score": round(combined_score, 2),
        "basic_score": basic["risk_score"],
        "advanced_score": advanced["risk_score"],
        "reasons": all_reasons,
        "action": action,
        "recommendations": generate_recommendations(all_reasons, combined_score)
    }


def generate_recommendations(reasons: list, score: float) -> list:
    """Generate user recommendations based on fraud analysis"""
    
    recommendations = []
    
    if score >= 0.7:
        recommendations.append("🚨 Do NOT proceed with this transaction")
        recommendations.append("🔒 Change your UPI PIN immediately")
        recommendations.append("📞 Call your bank if you didn't initiate this")
    elif score >= 0.4:
        recommendations.append("⚠️ Verify the recipient before confirming")
        recommendations.append("🔍 Check if you recognize this transaction")
    
    if any("velocity" in r.lower() for r in reasons):
        recommendations.append("⏸️ Slow down - too many transactions too quickly")
    
    if any("new payee" in r.lower() for r in reasons):
        recommendations.append("👤 Verify the new contact before sending money")
    
    if any("unusual hour" in r.lower() for r in reasons):
        recommendations.append("🌙 Be extra careful with late-night transactions")
    
    return recommendations

