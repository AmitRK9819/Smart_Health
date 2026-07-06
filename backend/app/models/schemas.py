"""
Pydantic schemas shared across routes.
"""

import datetime as _dt
from datetime import date as date_type, datetime
from typing import List

from pydantic import BaseModel, Field


# ── Inventory ────────────────────────────────────────────────────────────────

class SupplyItemBase(BaseModel):
    name: str = Field(..., examples=["N95 Respirator Mask"])
    category: str = Field(..., examples=["PPE"])
    quantity: int = Field(..., ge=0)
    unit: str = Field(default="units", examples=["units", "boxes", "liters"])
    reorder_level: int = Field(default=50, ge=0)
    supplier: str | None = None


class SupplyItemCreate(SupplyItemBase):
    pass


class SupplyItem(SupplyItemBase):
    id: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


# ── Users ────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    username: str
    email: str
    role: str = Field(default="viewer", examples=["admin", "manager", "viewer"])


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True


# ── Predictions ──────────────────────────────────────────────────────────────

class PredictionRequest(BaseModel):
    item_id: int
    horizon_days: int = Field(default=30, ge=1, le=365, description="Number of days to forecast")


class PredictionResponse(BaseModel):
    item_id: int
    item_name: str
    forecasted_demand: list[dict]
    anomaly_flags: list[dict] | None = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ── Footfall / Shortage Prediction ──────────────────────────────────────────

class FootfallEntry(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-06-15"])
    count: int = Field(..., ge=0, examples=[120])


class FootfallRequest(BaseModel):
    history: list[FootfallEntry] = Field(
        ...,
        min_length=1,
        description="Daily patient footfall history (date + count pairs)",
    )


# ── Health Centre Data ──────────────────────────────────────────────────────

class StockUpdate(BaseModel):
    """Represents a medicine stock update at a Primary Health Centre."""
    phc_id: str = Field(..., description="Primary Health Centre identifier")
    medicine_name: str = Field(..., description="Name of the medicine")
    quantity: int = Field(..., description="Stock quantity")
    timestamp: datetime = Field(..., description="Time of the stock update")


class DailyFootfall(BaseModel):
    """Daily patient footfall record for a Primary Health Centre."""
    phc_id: str = Field(..., description="Primary Health Centre identifier")
    date: date_type = Field(..., description="Date of the footfall record")
    patient_count: int = Field(..., ge=0, description="Number of patients")


class FootfallPredictionRequest(BaseModel):
    """Request payload for footfall-based predictions, wrapping a list of DailyFootfall entries."""
    footfall_data: List[DailyFootfall] = Field(
        ...,
        min_length=1,
        description="List of daily footfall records to base predictions on",
    )
