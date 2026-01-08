def classify_months(monthly_income: dict):
    """
    Classifies months into GOOD / BAD
    """

    if not monthly_income:
        return {}

    avg_income = sum(monthly_income.values()) / len(monthly_income)

    month_classification = {}

    for month, income in monthly_income.items():
        if income >= avg_income:
            month_classification[month] = "GOOD"
        else:
            month_classification[month] = "BAD"

    return month_classification
