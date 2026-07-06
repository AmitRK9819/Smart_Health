"""
Demand forecasting using Facebook Prophet.

Generates synthetic historical consumption data for a supply item,
fits a Prophet model, and returns a forecast for the requested horizon.
In production, replace the synthetic data with real consumption logs.

Also provides ``predict_demand`` — an async helper that predicts patient
footfall for the next 7 days, with a simple-moving-average fallback when
the input history is too short for Prophet (< 14 records).
"""

from __future__ import annotations

import asyncio
import logging
import math
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
from prophet import Prophet

logger = logging.getLogger(__name__)


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


# ── Patient Footfall Prediction ─────────────────────────────────────────────

_FORECAST_HORIZON = 7  # days to predict ahead
_MIN_RECORDS_FOR_PROPHET = 14  # Prophet needs at least ~2 weeks of data


def _run_prophet(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Fit Prophet on *df* (columns ``ds``, ``y``) and return 7-day forecast.

    This is a **synchronous** helper designed to be offloaded to a thread pool
    via :func:`asyncio.to_thread` so the event-loop stays responsive.
    """
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
    )
    # Suppress the verbose cmdstan output Prophet emits by default
    model.fit(df)

    future = model.make_future_dataframe(periods=_FORECAST_HORIZON)
    forecast = model.predict(future)

    rows = forecast.tail(_FORECAST_HORIZON)[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ]
    return [
        {
            "date": row["ds"].strftime("%Y-%m-%d"),
            "predicted_count": max(0, round(row["yhat"], 1)),
            "lower_bound": max(0, round(row["yhat_lower"], 1)),
            "upper_bound": max(0, round(row["yhat_upper"], 1)),
        }
        for _, row in rows.iterrows()
    ]


def _sma_fallback(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a flat 7-day forecast based on the simple moving average.

    Used when there are fewer than ``_MIN_RECORDS_FOR_PROPHET`` records,
    which is too few for Prophet to fit meaningfully.  The bounds are set
    to ±20 % of the SMA to give a rough uncertainty band.
    """
    counts = [r["patient_count"] for r in records]
    sma = sum(counts) / len(counts) if counts else 0.0
    margin = round(sma * 0.2, 1)

    last_date_str = max(r["date"] for r in records)
    # Accept both date objects and ISO-format strings
    if isinstance(last_date_str, date):
        last_date = last_date_str
    else:
        last_date = datetime.strptime(str(last_date_str), "%Y-%m-%d").date()

    result: list[dict[str, Any]] = []
    for day_offset in range(1, _FORECAST_HORIZON + 1):
        forecast_date = last_date + timedelta(days=day_offset)
        result.append(
            {
                "date": forecast_date.strftime("%Y-%m-%d"),
                "predicted_count": max(0, round(sma, 1)),
                "lower_bound": max(0, round(sma - margin, 1)),
                "upper_bound": round(sma + margin, 1),
            }
        )
    return result


async def predict_demand(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Predict patient footfall for the next 7 days.

    Parameters
    ----------
    records:
        A list of dictionaries, each containing:
        - ``date``  — a date string (``YYYY-MM-DD``) or :class:`datetime.date`
        - ``patient_count`` — an integer with that day's patient count

    Returns
    -------
    list[dict]
        Seven dictionaries with keys ``date``, ``predicted_count``,
        ``lower_bound``, and ``upper_bound``.

    Notes
    -----
    * When ``len(records) >= 14`` the function fits a Prophet model (off the
      main thread) and returns its 7-day forecast with uncertainty intervals.
    * When ``len(records) < 14`` it falls back to a flat prediction based on
      the Simple Moving Average with ±20 % bounds.
    """
    if not records:
        raise ValueError("records must be a non-empty list")

    # ── Fallback: too few data points for Prophet ────────────────────────
    if len(records) < _MIN_RECORDS_FOR_PROPHET:
        logger.info(
            "Only %d record(s) received (< %d) — using SMA fallback.",
            len(records),
            _MIN_RECORDS_FOR_PROPHET,
        )
        return _sma_fallback(records)

    # ── Full Prophet forecast ────────────────────────────────────────────
    logger.info(
        "Received %d records — fitting Prophet model.", len(records)
    )

    # Build the DataFrame Prophet expects (columns: ds, y)
    df = pd.DataFrame(
        {
            "ds": pd.to_datetime(
                [r["date"] for r in records], format="%Y-%m-%d"
            ),
            "y": [r["patient_count"] for r in records],
        }
    )

    # Run the CPU-bound Prophet fit in a thread so we don't block the
    # async event-loop.
    return await asyncio.to_thread(_run_prophet, df)
