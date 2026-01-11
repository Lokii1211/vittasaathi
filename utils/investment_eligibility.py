def check_investment_eligibility(stability_score, prediction):
    if stability_score < 40:
        return {
            "eligible": False,
            "reason": "Income too irregular for investments"
        }

    if prediction["worst_case_income"] < prediction["expected_income"] * 0.6:
        return {
            "eligible": False,
            "reason": "High income uncertainty detected"
        }

    return {
        "eligible": True,
        "risk_level": (
            "LOW" if stability_score >= 70
            else "MEDIUM"
        )
    }

