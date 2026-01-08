def calculate_safe_emi(monthly_income: float) -> float:
    """
    EMI should not exceed 30% of income
    """
    return round(monthly_income * 0.30, 2)


def loan_amount_from_emi(emi: float, months: int = 24, interest_rate: float = 0.14):
    """
    Rough loan amount estimation from EMI
    """
    r = interest_rate / 12
    loan_amount = emi * ((1 + r) ** months - 1) / (r * (1 + r) ** months)
    return round(loan_amount, 2)


def loan_decision(stability_score: float):
    """
    Decide loan category based on stability
    """
    if stability_score < 0.4:
        return "LOW"
    elif stability_score < 0.7:
        return "MEDIUM"
    else:
        return "HIGH"
