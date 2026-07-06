"""
Inventory management routes.

Provides CRUD endpoints for healthcare supply items
(masks, gloves, syringes, medications, etc.).

Also exposes PHC-specific endpoints for Member 4 (DB integration):
  POST /inventory/update          – log a stock update (stub; DB TBD)
  GET  /inventory/status/{phc_id} – current stock levels for a PHC
"""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import SupplyItem, SupplyItemCreate, StockUpdate

router = APIRouter(prefix="/inventory", tags=["Inventory"])

# ── In-memory store (replace with a real DB later) ───────────────────────────

_inventory: dict[int, SupplyItem] = {}
_next_id: int = 1


def _seed_demo_data() -> None:
    """Populate a handful of demo items on first import."""
    global _next_id
    demo_items = [
        SupplyItemCreate(name="N95 Respirator Mask", category="PPE", quantity=1200, unit="units", reorder_level=200, supplier="3M Healthcare"),
        SupplyItemCreate(name="Nitrile Exam Gloves", category="PPE", quantity=5000, unit="boxes", reorder_level=500, supplier="Halyard Health"),
        SupplyItemCreate(name="Ibuprofen 200mg", category="Medication", quantity=340, unit="bottles", reorder_level=100, supplier="PharmaCorp"),
        SupplyItemCreate(name="IV Saline 0.9%", category="Fluids", quantity=800, unit="bags", reorder_level=150, supplier="Baxter"),
        SupplyItemCreate(name="Disposable Syringes 5ml", category="Consumables", quantity=3000, unit="units", reorder_level=600, supplier="BD Medical"),
    ]
    for item_data in demo_items:
        item = SupplyItem(id=_next_id, **item_data.model_dump(), last_updated=datetime.utcnow())
        _inventory[_next_id] = item
        _next_id += 1


_seed_demo_data()


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[SupplyItem], summary="List all supply items")
async def list_items(
    category: str | None = Query(None, description="Filter by category"),
    low_stock: bool = Query(False, description="Show only items below reorder level"),
):
    items = list(_inventory.values())
    if category:
        items = [i for i in items if i.category.lower() == category.lower()]
    if low_stock:
        items = [i for i in items if i.quantity <= i.reorder_level]
    return items


@router.get("/{item_id}", response_model=SupplyItem, summary="Get a single supply item")
async def get_item(item_id: int):
    if item_id not in _inventory:
        raise HTTPException(status_code=404, detail="Item not found")
    return _inventory[item_id]


@router.post("/", response_model=SupplyItem, status_code=201, summary="Add a new supply item")
async def create_item(item_in: SupplyItemCreate):
    global _next_id
    item = SupplyItem(id=_next_id, **item_in.model_dump(), last_updated=datetime.utcnow())
    _inventory[_next_id] = item
    _next_id += 1
    return item


@router.put("/{item_id}", response_model=SupplyItem, summary="Update a supply item")
async def update_item(item_id: int, item_in: SupplyItemCreate):
    if item_id not in _inventory:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = SupplyItem(id=item_id, **item_in.model_dump(), last_updated=datetime.utcnow())
    _inventory[item_id] = updated
    return updated


@router.delete("/{item_id}", status_code=204, summary="Delete a supply item")
async def delete_item(item_id: int):
    if item_id not in _inventory:
        raise HTTPException(status_code=404, detail="Item not found")
    del _inventory[item_id]


# ── PHC Stock Endpoints (Member 4 will wire DB here) ─────────────────────────

# ---------------------------------------------------------------------------
# Mock stock data keyed by PHC ID.
# Each entry follows the StockLevel structure:
#   { medicine_name: { quantity, unit, reorder_level, status } }
# Member 4: replace this dict (or its lookup) with real DB queries.
# ---------------------------------------------------------------------------

_MOCK_PHC_STOCK: Dict[str, Dict] = {
    "PHC-001": {
        "Paracetamol": {
            "quantity": 520,
            "unit": "tablets",
            "reorder_level": 200,
            "status": "adequate",
        },
        "ORS": {
            "quantity": 85,
            "unit": "sachets",
            "reorder_level": 100,
            "status": "low",
        },
        "Anti-venom": {
            "quantity": 12,
            "unit": "vials",
            "reorder_level": 10,
            "status": "adequate",
        },
    },
    "PHC-002": {
        "Paracetamol": {
            "quantity": 130,
            "unit": "tablets",
            "reorder_level": 200,
            "status": "low",
        },
        "ORS": {
            "quantity": 310,
            "unit": "sachets",
            "reorder_level": 100,
            "status": "adequate",
        },
        "Anti-venom": {
            "quantity": 3,
            "unit": "vials",
            "reorder_level": 10,
            "status": "critical",
        },
    },
    "PHC-003": {
        "Paracetamol": {
            "quantity": 0,
            "unit": "tablets",
            "reorder_level": 200,
            "status": "critical",
        },
        "ORS": {
            "quantity": 200,
            "unit": "sachets",
            "reorder_level": 100,
            "status": "adequate",
        },
        "Anti-venom": {
            "quantity": 18,
            "unit": "vials",
            "reorder_level": 10,
            "status": "adequate",
        },
    },
}

# Default fallback for any unknown PHC (keeps the endpoint from erroring).
_DEFAULT_STOCK: Dict = {
    "Paracetamol": {
        "quantity": 250,
        "unit": "tablets",
        "reorder_level": 200,
        "status": "adequate",
    },
    "ORS": {
        "quantity": 150,
        "unit": "sachets",
        "reorder_level": 100,
        "status": "adequate",
    },
    "Anti-venom": {
        "quantity": 8,
        "unit": "vials",
        "reorder_level": 10,
        "status": "low",
    },
}


@router.post(
    "/update",
    tags=["PHC Stock"],
    summary="Log a stock update for a PHC",
    response_description="Acknowledgement that the update was received",
)
async def update_stock(update: StockUpdate):
    """
    Accept a :class:`StockUpdate` payload and log it to the console.

    **Member 4 hook**: replace the ``print`` statement below with your
    database write (e.g. ``db.add(StockUpdateModel(**update.model_dump()))``).
    """
    # ── TODO (Member 4): persist `update` to the database ─────────────────
    print(
        f"[STOCK UPDATE] PHC={update.phc_id!r} | "
        f"Medicine={update.medicine_name!r} | "
        f"Qty={update.quantity} | "
        f"Timestamp={update.timestamp.isoformat()}"
    )
    # ──────────────────────────────────────────────────────────────────────

    return {"status": "success", "message": "Stock logged"}


@router.get(
    "/status/{phc_id}",
    tags=["PHC Stock"],
    summary="Get current stock levels for a PHC",
    response_description=(
        "A mapping of medicine name to its current stock details "
        "(quantity, unit, reorder_level, status)"
    ),
)
async def get_phc_stock_status(phc_id: str):
    """
    Return the current stock levels for **Paracetamol**, **ORS**, and
    **Anti-venom** at the requested Primary Health Centre.

    **Member 4 hook**: replace the mock-data lookup below with a real DB
    query filtered by ``phc_id``.

    ### Response structure
    ```json
    {
      "phc_id": "PHC-001",
      "stock": {
        "Paracetamol":  { "quantity": 520, "unit": "tablets",  "reorder_level": 200, "status": "adequate"  },
        "ORS":          { "quantity":  85, "unit": "sachets",  "reorder_level": 100, "status": "low"       },
        "Anti-venom":   { "quantity":  12, "unit": "vials",    "reorder_level":  10, "status": "adequate"  }
      },
      "last_updated": "2026-07-06T06:30:00Z"
    }
    ```

    Possible ``status`` values:
    - **`"adequate"`** – stock is above the reorder level
    - **`"low"`** – stock is at or below the reorder level
    - **`"critical"`** – stock is at zero or dangerously low
    """
    # ── TODO (Member 4): query DB for this phc_id instead of mock data ────
    stock_data = _MOCK_PHC_STOCK.get(phc_id.upper(), _DEFAULT_STOCK)
    # ──────────────────────────────────────────────────────────────────────

    return {
        "phc_id": phc_id.upper(),
        "stock": stock_data,
        "last_updated": datetime.utcnow().isoformat() + "Z",
    }
