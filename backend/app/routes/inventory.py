"""
Inventory management routes.

Provides CRUD endpoints for healthcare supply items
(masks, gloves, syringes, medications, etc.).
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import SupplyItem, SupplyItemCreate

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
