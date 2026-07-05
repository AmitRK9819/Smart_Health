"""
Asynchronous patient-footfall forecasting.

Predicts the next 7 days of daily patient footfall using Facebook Prophet.
Falls back to a 3-day simple moving average when the dataset is too small
(< 14 points) to train a reliable Prophet model.

Usage
-----
    result = await forecast_footfall([
        {"date": "2026-06-01", "count": 120},
        {"date": "2026-06-02", "count": 135},
        ...
    ])
"""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from prophet import Prophet

logger = logging.getLogger(__name__)

# A dedicated thread pool for CPU-bound Prophet work so the async
# event loop is never blocked.
_prophet_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="prophet")

# ── Constants ────────────────────────────────────────────────────────────────

FORECAST_HORIZON = 7           # days to predict
MIN_DATAPOINTS_FOR_PROPHET = 14  # Prophet needs a reasonable history
SMA_WINDOW = 3                 # window size for the moving-average fallback


# ── Public API ───────────────────────────────────────────────────────────────

async def forecast_footfall(
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Forecast the next 7 days of patient footfall.

    Parameters
    ----------
    history : list[dict]
        Each dict must contain:
        - ``"date"``  – ISO-format date string (``YYYY-MM-DD``)
        - ``"count"`` – integer patient count for that day

    Returns
    -------
    dict
        {
            "method": "prophet" | "simple_moving_average",
            "horizon_days": 7,
            "input_points": <int>,
            "predictions": [
                {"date": "YYYY-MM-DD", "predicted_count": <float>},
                ...
            ]
        }

    Raises
    ------
    ValueError
        If ``history`` is empty or contains invalid entries.
    """
    _validate_input(history)

    if len(history) < MIN_DATAPOINTS_FOR_PROPHET:
        logger.info(
            "Only %d data points provided (need %d for Prophet) — "
            "falling back to %d-day simple moving average.",
            len(history),
            MIN_DATAPOINTS_FOR_PROPHET,
            SMA_WINDOW,
        )
        predictions = _sma_fallback(history)
        method = "simple_moving_average"
    else:
        # Offload the CPU-heavy Prophet fit/predict to a thread so
        # the async event loop stays responsive.
        predictions = await asyncio.get_running_loop().run_in_executor(
            _prophet_executor,
            _prophet_forecast,
            history,
        )
        method = "prophet"

    return {
        "method": method,
        "horizon_days": FORECAST_HORIZON,
        "input_points": len(history),
        "predictions": predictions,
    }


# ── Input validation ─────────────────────────────────────────────────────────

def _validate_input(history: list[dict[str, Any]]) -> None:
    """Raise ``ValueError`` on empty or malformed input."""
    if not history:
        raise ValueError("History list must not be empty.")

    for idx, entry in enumerate(history):
        if "date" not in entry or "count" not in entry:
            raise ValueError(
                f"Entry at index {idx} is missing required keys "
                f"'date' and/or 'count': {entry!r}"
            )
        # Quick date parse check
        try:
            datetime.strptime(str(entry["date"]), "%Y-%m-%d")
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Entry at index {idx} has an invalid date "
                f"'{entry['date']}'. Expected YYYY-MM-DD."
            ) from exc

        if not isinstance(entry["count"], (int, float)) or entry["count"] < 0:
            raise ValueError(
                f"Entry at index {idx} has an invalid count "
                f"'{entry['count']}'. Must be a non-negative number."
            )


# ── Prophet path ─────────────────────────────────────────────────────────────

def _prophet_forecast(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Fit a Prophet model on the historical footfall and predict the next
    ``FORECAST_HORIZON`` days.  Runs synchronously (called inside the
    thread-pool executor).
    """
    df = pd.DataFrame(history).rename(columns={"date": "ds", "count": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    df = df.sort_values("ds").reset_index(drop=True)

    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        uncertainty_samples=500,
    )

    # Suppress Prophet/cmdstanpy verbose stdout during fitting
    import logging as _logging
    for _name in ("prophet", "cmdstanpy"):
        _logging.getLogger(_name).setLevel(_logging.WARNING)
    model.fit(df)

    future = model.make_future_dataframe(periods=FORECAST_HORIZON)
    forecast = model.predict(future)

    # Extract only the forecasted window
    forecast_window = forecast.tail(FORECAST_HORIZON)[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ]

    return [
        {
            "date": row["ds"].strftime("%Y-%m-%d"),
            "predicted_count": round(max(row["yhat"], 0), 1),
            "lower_bound": round(max(row["yhat_lower"], 0), 1),
            "upper_bound": round(max(row["yhat_upper"], 0), 1),
        }
        for _, row in forecast_window.iterrows()
    ]


# ── SMA fallback path ───────────────────────────────────────────────────────

def _sma_fallback(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Simple moving-average fallback when there are fewer than
    ``MIN_DATAPOINTS_FOR_PROPHET`` data points.

    Takes the mean of the last ``SMA_WINDOW`` days (or fewer if the
    history is shorter) and projects it flat for ``FORECAST_HORIZON`` days.
    """
    sorted_history = sorted(history, key=lambda x: x["date"])
    recent = sorted_history[-SMA_WINDOW:]
    avg = sum(entry["count"] for entry in recent) / len(recent)

    last_date = datetime.strptime(sorted_history[-1]["date"], "%Y-%m-%d")

    return [
        {
            "date": (last_date + timedelta(days=i + 1)).strftime("%Y-%m-%d"),
            "predicted_count": round(avg, 1),
            "lower_bound": None,
            "upper_bound": None,
        }
        for i in range(FORECAST_HORIZON)
    ]
