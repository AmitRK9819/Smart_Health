"""
Anomaly detection for supply-chain consumption patterns.

Uses scikit-learn's Isolation Forest to flag unusual consumption
spikes or drops.  In production, feed real transaction data.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def _generate_synthetic_transactions(
    item_id: int,
    current_quantity: int,
    days: int = 90,
) -> pd.DataFrame:
    """
    Build synthetic daily usage data with a few injected anomalies.
    Replace with real transaction queries in production.
    """
    np.random.seed(item_id + 1000)
    base = max(current_quantity / 30, 5)

    dates = [datetime.utcnow() - timedelta(days=days - i) for i in range(days)]
    usages = np.random.normal(base, base * 0.15, size=days)

    # Inject 2-3 anomalies
    anomaly_indices = np.random.choice(days, size=3, replace=False)
    for idx in anomaly_indices:
        usages[idx] *= np.random.choice([2.5, 0.1])  # spike or near-zero

    usages = np.clip(usages, 0, None)

    return pd.DataFrame({"date": dates, "usage": usages})


def detect_anomalies(
    item_id: int,
    item_name: str,
    current_quantity: int,
) -> list[dict]:
    """
    Return a list of flagged anomalous days:
    [{date, usage, anomaly_score, flag}]
    """
    df = _generate_synthetic_transactions(item_id, current_quantity)

    features = df[["usage"]].values
    model = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
    df["anomaly_label"] = model.fit_predict(features)  # 1 = normal, -1 = anomaly
    df["anomaly_score"] = model.decision_function(features)

    anomalies = df[df["anomaly_label"] == -1].copy()
    return [
        {
            "date": row["date"].strftime("%Y-%m-%d"),
            "usage": round(row["usage"], 1),
            "anomaly_score": round(row["anomaly_score"], 4),
            "flag": "unusual_spike" if row["usage"] > df["usage"].mean() else "unusual_drop",
        }
        for _, row in anomalies.iterrows()
    ]


def detect_footfall_anomaly(history_records: list[dict]) -> bool:
    """
    Detect if the most recent daily footfall count is statistically
    irregular compared to the historical trend using Isolation Forest.
    
    Parameters
    ----------
    history_records : list[dict]
        List of historical footfall records, e.g. 
        [{"date": "2026-07-01", "patient_count": 120}, ...]
        Assumes the records are ordered chronologically and the last 
        element is "today".
        
    Returns
    -------
    bool
        True if the most recent record is an anomaly, False otherwise.
    """
    if not history_records or len(history_records) < 14:
        # Not enough data to build a reliable baseline
        return False
        
    df = pd.DataFrame(history_records)
    if "patient_count" not in df.columns:
        return False
        
    features = df[["patient_count"]].values
    
    # We use contamination="auto" or a fixed rate. 0.05 means 5% of data is expected to be anomaly.
    model = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
    
    # Fit the model and predict anomalies (1 = normal, -1 = anomaly)
    anomaly_labels = model.fit_predict(features)
    
    # Check the last record ("today")
    is_anomaly = anomaly_labels[-1] == -1
    return bool(is_anomaly)
