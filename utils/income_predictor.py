from prophet import Prophet

def predict_next_month_income(df):
    """
    Takes daily income DataFrame
    Returns next month prediction with confidence
    """

    if df is None or len(df) < 10:
        return {
            "status": "not_enough_data",
            "message": "At least 10 days of income data required"
        }

    # Initialize Prophet model
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True
    )

    # Train model
    model.fit(df)

    # Predict next 30 days
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    # Extract next 30 days
    next_30 = forecast.tail(30)

    expected_income = next_30["yhat"].sum()
    best_case = next_30["yhat_upper"].sum()
    worst_case = next_30["yhat_lower"].sum()

    confidence = round(
        (expected_income - worst_case) / expected_income * 100, 2
    ) if expected_income > 0 else 0

    return {
        "expected_income": round(expected_income, 2),
        "best_case_income": round(best_case, 2),
        "worst_case_income": round(worst_case, 2),
        "confidence_percent": confidence
    }

