def investment_allocation(stability_score):
    if stability_score >= 70:
        return {
            "equity": "60%",
            "debt": "30%",
            "emergency_fund": "10%"
        }

    return {
        "equity": "40%",
        "debt": "40%",
        "emergency_fund": "20%"
    }
