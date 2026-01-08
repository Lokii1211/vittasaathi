def calculate_safe_emi(prediction: dict):
    """
    Calculates safe and aggressive EMI amounts
    """

    if "worst_case_income" not in prediction:
        return None

    worst_case = prediction["worst_case_income"]
    expected = prediction["expected_income"]

    safe_emi = round(worst_case * 0.30, 2)
    aggressive_emi = round(expected * 0.40, 2)

    return {
        "safe_emi": safe_emi,
        "aggressive_emi": aggressive_emi
    }
