def should_pause_investment(prediction, current_sip):
    if prediction["worst_case_income"] < (current_sip * 4):
        return {
            "pause": True,
            "reason": "Income dropped below safe investment threshold"
        }

    return {
        "pause": False
    }

