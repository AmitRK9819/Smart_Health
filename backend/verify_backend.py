"""
verify_backend.py
=================

Sends a mock FootfallPredictionRequest (30 days of DailyFootfall data) to the
running FastAPI server and verifies it returns a valid 7-day forecast.

Usage
-----
    # Terminal 1 - start the server
    cd backend
    uvicorn main:app --reload

    # Terminal 2 - run this script
    python verify_backend.py
"""

import json
import random
import sys
from datetime import date, datetime, timedelta

import requests

# ── Configuration ────────────────────────────────────────────────────────────

BASE_URL = "http://127.0.0.1:8000"
# shortage_router is mounted at /api in main.py --> endpoint is /api/predict
PREDICT_URL = f"{BASE_URL}/api/predict"

DAYS_OF_HISTORY = 30
MIN_PATIENT_COUNT = 40
MAX_PATIENT_COUNT = 100
EXPECTED_FORECAST_DAYS = 7


def build_payload() -> dict:
    """Generate 30 days of mock DailyFootfall records ending today."""
    today = date.today()
    footfall_data = []
    for offset in range(DAYS_OF_HISTORY, 0, -1):
        record_date = today - timedelta(days=offset)
        footfall_data.append(
            {
                "phc_id": "PHC-TEST-001",
                "date": record_date.isoformat(),
                "patient_count": random.randint(
                    MIN_PATIENT_COUNT, MAX_PATIENT_COUNT
                ),
            }
        )
    return {"footfall_data": footfall_data}


def main() -> None:
    print("=" * 60)
    print("  verify_backend.py — Footfall Prediction Smoke Test")
    print("=" * 60)

    # ── Build payload ────────────────────────────────────────────────────
    payload = build_payload()
    print(
        f"\n[OK] Generated {len(payload['footfall_data'])} days of mock footfall "
        f"data (patient_count {MIN_PATIENT_COUNT}-{MAX_PATIENT_COUNT})."
    )
    print(f"  Date range: {payload['footfall_data'][0]['date']} --> "
          f"{payload['footfall_data'][-1]['date']}")

    # ── POST request ─────────────────────────────────────────────────────
    print(f"\n--> POST {PREDICT_URL}")
    try:
        response = requests.post(PREDICT_URL, json=payload, timeout=60)
    except requests.ConnectionError:
        print(
            "\n[FAIL] FAILURE: Could not connect to the server.\n"
            "  Make sure the FastAPI server is running:\n"
            "    cd backend && uvicorn main:app --reload"
        )
        sys.exit(1)

    # ── Assert status code ───────────────────────────────────────────────
    print(f"  Status code: {response.status_code}")
    assert response.status_code == 200, (
        f"Expected 200 OK but got {response.status_code}.\n"
        f"Response body: {response.text}"
    )
    print("  [OK] Status code is 200")

    # ── Print raw JSON response ──────────────────────────────────────────
    resp_json = response.json()
    print("\n── Raw JSON Response ──────────────────────────────────────")
    print(json.dumps(resp_json, indent=2))
    print("───────────────────────────────────────────────────────────")

    # ── Validate response structure ──────────────────────────────────────
    assert "predictions" in resp_json, "Missing 'predictions' key in response"

    predictions = resp_json["predictions"]
    assert len(predictions) == EXPECTED_FORECAST_DAYS, (
        f"Expected {EXPECTED_FORECAST_DAYS} predictions, got {len(predictions)}"
    )

    required_keys = {"date", "predicted_count", "lower_bound", "upper_bound"}
    for idx, pred in enumerate(predictions):
        missing = required_keys - set(pred.keys())
        assert not missing, (
            f"Prediction [{idx}] is missing keys: {missing}"
        )

    print(f"\n[OK] SUCCESS: Received {len(predictions)}-day forecast. "
          "All assertions passed.")


if __name__ == "__main__":
    main()
