def calculate_sip_amount(prediction, stability_score):
    expected = prediction["expected_income"]
    worst_case = prediction["worst_case_income"]

    if stability_score >= 70:
        sip = expected * 0.15   # 15%
    else:
        sip = worst_case * 0.08  # 8%

    return round(sip, 2)

