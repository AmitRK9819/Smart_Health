"""
Prediction / forecasting routes.

Exposes the ML pipeline (Prophet demand forecasting + scikit-learn anomaly
detection) through REST endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    FootfallPredictionRequest,
    FootfallRequest,
    PredictionRequest,
    PredictionResponse,
)
from app.ml.forecaster import forecast_demand, predict_demand as predict_footfall_demand
from app.ml.forecast import forecast_footfall
from app.ml.anomaly_detector import detect_anomalies, detect_footfall_anomaly
from app.ml.routing import calculate_transfers
from app.routes.inventory import _inventory, _MOCK_PHC_STOCK

router = APIRouter(prefix="/predictions", tags=["Predictions"])

# ── Mock GPS coordinates ──────────────────────────────────────────────────────
# Member 4 hook: replace with a real DB query:
#   SELECT phc_id, lat, lon FROM phcs
_PHC_COORDINATES: dict[str, dict[str, float]] = {
    "PHC-001": {"lat": 12.9716, "lon": 77.5946},   # Bangalore Urban
    "PHC-002": {"lat": 13.0827, "lon": 77.6310},   # Bangalore North
    "PHC-003": {"lat": 12.8456, "lon": 77.6603},   # Bangalore South
}


# ── Helper ────────────────────────────────────────────────────────────────────

def _build_inventory_snapshot() -> list[dict]:
    """
    Assemble the list of PHC inventory snapshots expected by
    ``calculate_transfers`` from the existing mock stock data and the
    coordinate table.

    Member 4 hook: replace ``_MOCK_PHC_STOCK`` / ``_PHC_COORDINATES``
    lookups with real DB queries when live data is available.
    """
    snapshots = []
    for phc_id, medicines in _MOCK_PHC_STOCK.items():
        location = _PHC_COORDINATES.get(
            phc_id,
            {"lat": 0.0, "lon": 0.0},  # graceful fallback for unknown PHCs
        )
        inventory = [
            {"medicine": med_name, "quantity": med_data["quantity"]}
            for med_name, med_data in medicines.items()
        ]
        snapshots.append(
            {
                "phc_id": phc_id,
                "location": location,
                "inventory": inventory,
            }
        )
    return snapshots


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/demand", response_model=PredictionResponse, summary="Forecast demand for a supply item")
async def predict_demand(req: PredictionRequest):
    if req.item_id not in _inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    item = _inventory[req.item_id]

    forecast = forecast_demand(
        item_id=req.item_id,
        item_name=item.name,
        current_quantity=item.quantity,
        horizon_days=req.horizon_days,
    )

    anomalies = detect_anomalies(
        item_id=req.item_id,
        item_name=item.name,
        current_quantity=item.quantity,
    )

    return PredictionResponse(
        item_id=req.item_id,
        item_name=item.name,
        forecasted_demand=forecast,
        anomaly_flags=anomalies,
    )


@router.get("/health", summary="ML pipeline health check")
async def ml_health():
    return {
        "status": "ok",
        "models": {
            "forecaster": "prophet",
            "anomaly_detector": "isolation_forest",
        },
    }


@router.get(
    "/recommend-transfers",
    tags=["Transfer Routing"],
    summary="Recommend inter-PHC medicine transfers to resolve critical shortages",
    response_description=(
        "A list of recommended stock transfer actions, each specifying the "
        "donor PHC, recipient PHC, medicine, quantity, and distance."
    ),
)
async def recommend_transfers():
    """
    Fetch current stock levels for **all PHCs**, run the transfer-routing
    algorithm, and return a prioritised list of recommended stock moves.

    The routing algorithm:

    1. Identifies every (PHC, medicine) pair where stock is **below the
       critical threshold** (< 10 units by default).
    2. For each shortage, finds the **nearest PHC** (by great-circle distance)
       that holds a **surplus** of the same medicine (> 100 units).
    3. Recommends transferring a fixed batch (**50 units** by default) from
       the donor to the recipient.

    ### Response structure
    ```json
    {
      "transfer_count": 2,
      "message": "2 transfer(s) recommended.",
      "transfers": [
        {
          "from_phc":    "PHC-001",
          "to_phc":      "PHC-002",
          "medicine":    "Paracetamol",
          "quantity":    50,
          "distance_km": 12.47
        }
      ]
    }
    ```

    Returns an **empty** ``transfers`` list when all PHCs are adequately
    stocked.

    **Member 4 hook**: swap ``_build_inventory_snapshot()`` with a live DB
    query when real data is available.
    """
    try:
        inventory_snapshot = _build_inventory_snapshot()
        transfers = calculate_transfers(inventory_snapshot)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Transfer routing failed: {exc}",
        )

    count = len(transfers)
    message = (
        f"{count} transfer(s) recommended."
        if count
        else "All PHCs are adequately stocked. No transfers needed."
    )

    return {
        "transfer_count": count,
        "message": message,
        "transfers": transfers,
    }


# ── Shortage / Footfall prediction (standalone prefix) ──────────────────────
# Mounted separately at /api in main.py → final URL: /api/predict-shortage

shortage_router = APIRouter(tags=["Shortage Prediction"])


@shortage_router.post(
    "/predict-shortage",
    summary="Predict patient footfall shortage for the next 7 days",
    response_description="7-day footfall forecast with method metadata",
)
async def predict_shortage(body: FootfallRequest):
    """
    Accepts historical daily patient footfall and returns a 7-day forecast.

    - **≥ 14 data points** → Facebook Prophet time-series model
    - **< 14 data points** → 3-day simple moving average fallback
    """
    try:
        history_dicts = [entry.model_dump() for entry in body.history]
        result = await forecast_footfall(history_dicts)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@shortage_router.post(
    "/predict",
    summary="Predict patient footfall for the next 7 days",
    response_description="7-day footfall forecast with predicted counts and confidence bounds",
)
async def predict_footfall(body: FootfallPredictionRequest):
    """
    Accepts a list of **DailyFootfall** records and returns a 7-day forecast.

    - **≥ 14 records** → Facebook Prophet time-series model
    - **< 14 records** → Simple Moving Average fallback (±20 % bounds)

    Each returned item contains ``date``, ``predicted_count``,
    ``lower_bound``, and ``upper_bound``.
    """
    try:
        # Convert Pydantic models → plain dicts expected by predict_demand
        records = [
            {
                "date": entry.date.isoformat(),
                "patient_count": entry.patient_count,
            }
            for entry in body.footfall_data
        ]

        predictions = await predict_footfall_demand(records)
        is_anomaly = detect_footfall_anomaly(records)

        return {
            "is_anomaly": is_anomaly,
            "predictions": predictions
        }

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        )
