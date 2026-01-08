import statistics

def calculate_income_stability(monthly_income: dict):
    """
    Returns:
    - average income
    - volatility
    - stability score (0–100)
    """

    if len(monthly_income) < 2:
        return {
            "average_income": 0,
            "volatility": 0,
            "stability_score": 0,
            "remark": "Not enough data"
        }

    incomes = list(monthly_income.values())

    avg_income = statistics.mean(incomes)
    std_dev = statistics.stdev(incomes)

    # Volatility ratio
    volatility = std_dev / avg_income if avg_income > 0 else 0

    # Stability score (higher is better)
    stability_score = max(0, 100 - int(volatility * 100))

    if stability_score >= 70:
        remark = "Stable Income"
    elif stability_score >= 40:
        remark = "Moderately Irregular"
    else:
        remark = "Highly Irregular"

    return {
        "average_income": round(avg_income, 2),
        "volatility": round(volatility, 2),
        "stability_score": stability_score,
        "remark": remark
    }
