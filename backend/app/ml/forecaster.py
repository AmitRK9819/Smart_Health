"""
Demand forecasting using Facebook Prophet.

Generates synthetic historical consumption data for a supply item,
fits a Prophet model, and returns a forecast for the requested horizon.
In production, replace the synthetic data with real consumption logs.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from prophet import Prophet


def _generate_synthetic_history(
    item_id: int,
    current_quantity: int,
    days: int = 180,
) -> pd.DataFrame:
    """
    Build a realistic-looking consumption history.

    Uses a base rate derived from current stock plus weekly seasonality
    and random noise.  Replace this with actual DB queries in production.
    """
    np.random.seed(item_id)  # reproducible per item
    base_daily = max(current_quantity / 30, 5)

    dates = [datetime.utcnow() - timedelta(days=days - i) for i in range(days)]
    values = []
    for i, dt in enumerate(dates):
        seasonal = 1.0 + 0.15 * np.sin(2 * np.pi * dt.weekday() / 7)
        noise = np.random.normal(0, base_daily * 0.1)
        values.append(max(0, base_daily * seasonal + noise))

    return pd.DataFrame({"ds": dates, "y": values})


def forecast_demand(
    item_id: int,
    item_name: str,
    current_quantity: int,
    horizon_days: int = 30,
) -> list[dict]:
    """
    Return a list of {date, predicted_demand, lower_bound, upper_bound} dicts.
    """
    history = _generate_synthetic_history(item_id, current_quantity)

    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
    )
    model.fit(history)

    future = model.make_future_dataframe(periods=horizon_days)
    forecast = model.predict(future)

    # Return only the forecasted window (not the fitted history)
    result = forecast.tail(horizon_days)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    return [
        {
            "date": row["ds"].strftime("%Y-%m-%d"),
            "predicted_demand": round(row["yhat"], 1),
            "lower_bound": round(row["yhat_lower"], 1),
            "upper_bound": round(row["yhat_upper"], 1),
        }
        for _, row in result.iterrows()
    ]
