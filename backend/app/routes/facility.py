"""
Facility management routes.

Provides endpoints for updating Primary Health Centre facility statuses
like beds availability and doctor attendance.

All operations verify that the referenced PHC exists before writing.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import BedsUpdate, AttendanceUpdate
from app import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/facility", tags=["Facility"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _verify_phc_exists(phc_id: str) -> None:
    """Raise 400 if the given PHC ID does not exist in *facilities*."""
    try:
        check = db.fetch_one(
            "SELECT phc_id FROM facilities WHERE phc_id = %s", (phc_id,)
        )
    except Exception as e:
        logger.error("Failed to verify PHC %s: %s", phc_id, e)
        raise HTTPException(
            status_code=500, detail="Failed to verify facility"
        )
    if not check:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid PHC ID '{phc_id}'. Facility does not exist.",
        )


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "/",
    summary="List all facilities with stock, beds, and attendance",
    response_description="Array of facilities formatted for frontend dashboards",
)
async def list_facilities():
    """Return all facilities with their aggregated stock items, available beds, and doctor attendance.

    Formatted to seamlessly integrate with frontend dashboards.
    """
    try:
        facs = db.fetch_all("SELECT phc_id, facility_name, district, state, address, latitude, longitude, updated_at FROM facilities ORDER BY phc_id")
        meds = db.fetch_all("SELECT item_id, name, reorder_level, unit FROM medicines ORDER BY item_id")
        inv = db.fetch_all("SELECT phc_id, item_id, COALESCE(SUM(quantity), 0) AS quantity FROM inventory GROUP BY phc_id, item_id")
        beds = db.fetch_all("SELECT phc_id, available_beds FROM beds")
        # Get the latest attendance for each PHC (not just today)
        att = db.fetch_all("""
            SELECT DISTINCT ON (phc_id) phc_id, doctors_present
            FROM phc_attendance_summary
            ORDER BY phc_id, attendance_date DESC
        """)
        # Compute actual avg daily consumption from medicine_consumption table
        consumption = db.fetch_all("""
            SELECT phc_id, item_id,
                   COALESCE(AVG(quantity_consumed), 0) AS avg_daily
            FROM medicine_consumption
            WHERE consumption_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY phc_id, item_id
        """)

        inv_map = {(r["phc_id"], r["item_id"]): int(r["quantity"]) for r in inv}
        beds_map = {r["phc_id"]: int(r["available_beds"]) for r in beds}
        att_map = {r["phc_id"]: int(r["doctors_present"]) for r in att}
        cons_map = {(r["phc_id"], r["item_id"]): float(r["avg_daily"]) for r in consumption}

        result = []
        for f in facs:
            phc_id = f["phc_id"]
            stock_items = []
            for m in meds:
                qty = inv_map.get((phc_id, m["item_id"]), 0)
                # Use real consumption data, fall back to a small fraction of reorder level
                avg_cons = cons_map.get((phc_id, m["item_id"]), None)
                if avg_cons is None or avg_cons < 1:
                    avg_cons = max(1, int(m["reorder_level"] * 0.15))
                else:
                    avg_cons = int(avg_cons)
                stock_items.append({
                    "itemName": m["name"],
                    "currentUnits": qty,
                    "avgDailyConsumption": avg_cons,
                    "unit": m["unit"],
                    "reorderLevel": m["reorder_level"],
                })

            result.append({
                "id": phc_id,
                "name": f["facility_name"],
                "block": f["district"],
                "lat": float(f["latitude"]),
                "lng": float(f["longitude"]),
                "availableBeds": beds_map.get(phc_id, 0),
                "doctorsPresent": att_map.get(phc_id, 0),
                "stockItems": stock_items,
                "lastUpdated": str(f["updated_at"]),
            })
        return result
    except Exception as e:
        logger.error("Failed to list facilities: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list facilities")


@router.post(
    "/beds",
    summary="Log a beds availability update for a PHC",
    response_description="Acknowledgement that the update was received",
)
async def update_beds(update: BedsUpdate):
    """UPSERT available beds count for a PHC.

    Returns 400 if the PHC ID does not exist in the facilities table.
    """
    _verify_phc_exists(update.phc_id)

    query = """
    INSERT INTO beds (phc_id, available_beds, timestamp, updated_at)
    VALUES (%s, %s, %s, NOW())
    ON CONFLICT (phc_id) 
    DO UPDATE SET available_beds = EXCLUDED.available_beds,
                  timestamp     = EXCLUDED.timestamp,
                  updated_at    = NOW()
    """
    try:
        db.execute_query(
            query, (update.phc_id, update.available_beds, update.timestamp)
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "foreign key constraint" in error_msg:
            raise HTTPException(status_code=400, detail="Invalid PHC ID")
        logger.error("Failed to update beds for %s: %s", update.phc_id, e)
        raise HTTPException(
            status_code=500, detail="Failed to log beds update"
        )

    return {"status": "success", "message": "Beds update logged"}


@router.post(
    "/attendance",
    summary="Log a doctor attendance update for a PHC",
    response_description="Acknowledgement that the update was received",
)
async def update_attendance(update: AttendanceUpdate):
    """UPSERT daily doctor attendance summary for a PHC.

    Returns 400 if the PHC ID does not exist in the facilities table.
    """
    _verify_phc_exists(update.phc_id)

    attendance_date = update.timestamp.date()
    query = """
    INSERT INTO phc_attendance_summary
        (phc_id, attendance_date, doctors_present, timestamp, updated_at)
    VALUES (%s, %s, %s, %s, NOW())
    ON CONFLICT (phc_id, attendance_date)
    DO UPDATE SET doctors_present = EXCLUDED.doctors_present,
                  timestamp       = EXCLUDED.timestamp,
                  updated_at      = NOW()
    """
    try:
        db.execute_query(
            query,
            (update.phc_id, attendance_date, update.doctors_present, update.timestamp),
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "foreign key constraint" in error_msg:
            raise HTTPException(status_code=400, detail="Invalid PHC ID")
        logger.error(
            "Failed to update attendance for %s: %s", update.phc_id, e
        )
        raise HTTPException(
            status_code=500, detail="Failed to log attendance update"
        )

    return {"status": "success", "message": "Attendance update logged"}
