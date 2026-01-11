def calculate_loan_eligibility(stability_score, emi_data):
    """
    Calculates loan eligibility based on risk & EMI
    """

    if stability_score < 40:
        return {
            "eligible": False,
            "reason": "Income too irregular for loan"
        }

    # Assume 12, 24, 36 month options
    tenure_options = [12, 24, 36]

    loan_options = []

    for months in tenure_options:
        amount = emi_data["safe_emi"] * months
        loan_options.append({
            "tenure_months": months,
            "max_loan_amount": round(amount, 2)
        })

    risk_level = (
        "LOW" if stability_score >= 70
        else "MEDIUM" if stability_score >= 50
        else "HIGH"
    )

    return {
        "eligible": True,
        "risk_level": risk_level,
        "loan_options": loan_options
    }

