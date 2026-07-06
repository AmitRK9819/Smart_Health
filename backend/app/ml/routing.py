"""
Inventory transfer routing for PHC (Primary Health Centre) stock rebalancing.

``calculate_transfers`` inspects a snapshot of multi-PHC inventory levels,
identifies PHCs whose stock of any medicine has fallen below a critical
threshold, and recommends transfers from the geographically nearest PHC
that currently holds a surplus of the same medicine.

Distance between PHCs is computed with the Haversine formula so that the
routing logic works correctly with real GPS coordinates.

Usage
-----
    transfers = calculate_transfers([
        {
            "phc_id": "PHC_A",
            "location": {"lat": 12.97, "lon": 77.59},
            "inventory": [
                {"medicine": "Paracetamol", "quantity": 5},
                {"medicine": "ORS",         "quantity": 200},
            ],
        },
        ...
    ])
    # [{'from_phc': 'PHC_B', 'to_phc': 'PHC_A',
    #   'medicine': 'Paracetamol', 'quantity': 50, 'distance_km': 3.72}]
"""

from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)

# ── Thresholds ────────────────────────────────────────────────────────────────

#: A PHC is *critical* for a medicine when its stock falls below this value.
CRITICAL_THRESHOLD: int = 10

#: A PHC has a *surplus* for a medicine when its stock exceeds this value.
SURPLUS_THRESHOLD: int = 100

#: Units to transfer when a rebalancing move is recommended.
TRANSFER_QUANTITY: int = 50


# ── Public API ────────────────────────────────────────────────────────────────


def calculate_transfers(
    current_inventory_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Recommend stock transfers between PHCs to resolve critical shortages.

    The function iterates over every (PHC, medicine) pair that is below the
    ``CRITICAL_THRESHOLD`` and pairs it with the *nearest* PHC (by great-circle
    distance) that holds a surplus of the same medicine above
    ``SURPLUS_THRESHOLD``.  Each pair produces one transfer recommendation
    carrying ``TRANSFER_QUANTITY`` units.

    Parameters
    ----------
    current_inventory_data : list[dict]
        A list of PHC inventory snapshots.  Each snapshot must contain:

        ``"phc_id"`` : str
            Unique identifier for the PHC (e.g. ``"PHC_Kolar_01"``).

        ``"location"`` : dict
            GPS coordinates with keys ``"lat"`` (latitude) and
            ``"lon"`` (longitude), both as floats.

        ``"inventory"`` : list[dict]
            Per-medicine stock entries, each with:

            - ``"medicine"`` (str): medicine name.
            - ``"quantity"`` (int | float): current units on hand.

    Returns
    -------
    list[dict]
        A (possibly empty) list of recommended transfer dicts, each with:

        - ``"from_phc"``    – ID of the donor PHC
        - ``"to_phc"``      – ID of the recipient PHC
        - ``"medicine"``    – name of the medicine to transfer
        - ``"quantity"``    – number of units to transfer
        - ``"distance_km"`` – great-circle distance between the two PHCs
          (rounded to 2 decimal places)

    Raises
    ------
    ValueError
        If ``current_inventory_data`` is empty or any entry is missing
        required fields.

    Examples
    --------
    >>> data = [
    ...     {
    ...         "phc_id": "PHC_A",
    ...         "location": {"lat": 12.97, "lon": 77.59},
    ...         "inventory": [{"medicine": "Paracetamol", "quantity": 5}],
    ...     },
    ...     {
    ...         "phc_id": "PHC_B",
    ...         "location": {"lat": 13.00, "lon": 77.60},
    ...         "inventory": [{"medicine": "Paracetamol", "quantity": 200}],
    ...     },
    ... ]
    >>> transfers = calculate_transfers(data)
    >>> transfers[0]["from_phc"]
    'PHC_B'
    >>> transfers[0]["to_phc"]
    'PHC_A'
    >>> transfers[0]["medicine"]
    'Paracetamol'
    >>> transfers[0]["quantity"]
    50
    """
    _validate_inventory_data(current_inventory_data)

    # phc_map[phc_id] = full snapshot dict (fast O(1) lookups)
    phc_map: dict[str, dict[str, Any]] = {
        entry["phc_id"]: entry for entry in current_inventory_data
    }

    # stock_map[(phc_id, medicine)] = quantity
    stock_map: dict[tuple[str, str], float] = {}
    for entry in current_inventory_data:
        for item in entry["inventory"]:
            stock_map[(entry["phc_id"], item["medicine"])] = item["quantity"]

    # ── Step 1: find all critical (phc_id, medicine) pairs ───────────────────
    critical_pairs: list[tuple[str, str]] = [
        (phc_id, medicine)
        for (phc_id, medicine), qty in stock_map.items()
        if qty < CRITICAL_THRESHOLD
    ]

    if not critical_pairs:
        logger.info(
            "No PHC is below the critical threshold (%d units). "
            "No transfers needed.",
            CRITICAL_THRESHOLD,
        )
        return []

    # ── Step 2: build a per-medicine index of surplus PHC IDs ─────────────────
    # surplus_index[medicine] = [phc_id, ...]
    surplus_index: dict[str, list[str]] = {}
    for (phc_id, medicine), qty in stock_map.items():
        if qty > SURPLUS_THRESHOLD:
            surplus_index.setdefault(medicine, []).append(phc_id)

    # ── Step 3: for each critical pair, find the nearest donor ────────────────
    transfers: list[dict[str, Any]] = []

    for critical_phc_id, medicine in critical_pairs:
        donor_phc_ids = surplus_index.get(medicine, [])

        if not donor_phc_ids:
            logger.warning(
                "PHC '%s' is critically low on '%s' (< %d units) "
                "but no surplus donor PHC found.",
                critical_phc_id,
                medicine,
                CRITICAL_THRESHOLD,
            )
            continue

        critical_location = phc_map[critical_phc_id]["location"]
        nearest_donor, distance_km = _find_nearest(
            critical_location, donor_phc_ids, phc_map
        )

        transfer: dict[str, Any] = {
            "from_phc": nearest_donor,
            "to_phc": critical_phc_id,
            "medicine": medicine,
            "quantity": TRANSFER_QUANTITY,
            "distance_km": round(distance_km, 2),
        }
        transfers.append(transfer)

        logger.info(
            "Transfer recommended: %d units of '%s' from '%s' → '%s' "
            "(%.2f km apart).",
            TRANSFER_QUANTITY,
            medicine,
            nearest_donor,
            critical_phc_id,
            distance_km,
        )

    return transfers


# ── Private helpers ───────────────────────────────────────────────────────────


def _haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Return the great-circle distance in kilometres between two GPS points
    using the Haversine formula.

    Parameters
    ----------
    lat1, lon1 : float
        Coordinates of the first point in decimal degrees.
    lat2, lon2 : float
        Coordinates of the second point in decimal degrees.
    """
    R = 6_371.0  # Earth's mean radius in km

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _find_nearest(
    origin: dict[str, float],
    candidate_phc_ids: list[str],
    phc_map: dict[str, dict[str, Any]],
) -> tuple[str, float]:
    """
    Return the ``(phc_id, distance_km)`` of the PHC nearest to ``origin``
    among the candidates.

    Parameters
    ----------
    origin : dict
        ``{"lat": float, "lon": float}`` coordinates of the reference PHC.
    candidate_phc_ids : list[str]
        Non-empty list of donor PHC IDs to evaluate.
    phc_map : dict
        Full PHC snapshot dictionary keyed by PHC ID.
    """
    best_id: str | None = None
    best_dist = math.inf

    for phc_id in candidate_phc_ids:
        loc = phc_map[phc_id]["location"]
        dist = _haversine_km(
            origin["lat"], origin["lon"],
            loc["lat"], loc["lon"],
        )
        if dist < best_dist:
            best_dist = dist
            best_id = phc_id

    # caller guarantees candidate_phc_ids is non-empty
    return best_id, best_dist  # type: ignore[return-value]


def _validate_inventory_data(data: list[dict[str, Any]]) -> None:
    """
    Raise ``ValueError`` if ``data`` is empty or structurally invalid.

    Checks for required top-level keys (``phc_id``, ``location``,
    ``inventory``), valid GPS coordinates, and valid per-medicine stock
    entries.
    """
    if not data:
        raise ValueError("current_inventory_data must not be empty.")

    for idx, entry in enumerate(data):
        for required_key in ("phc_id", "location", "inventory"):
            if required_key not in entry:
                raise ValueError(
                    f"Entry at index {idx} is missing required key "
                    f"'{required_key}': {entry!r}"
                )

        loc = entry["location"]
        if not isinstance(loc, dict) or "lat" not in loc or "lon" not in loc:
            raise ValueError(
                f"Entry at index {idx} has an invalid 'location'. "
                f"Expected a dict with 'lat' and 'lon' keys, got: {loc!r}"
            )

        if not isinstance(entry["inventory"], list):
            raise ValueError(
                f"Entry at index {idx} 'inventory' must be a list, "
                f"got: {type(entry['inventory']).__name__!r}"
            )

        for item_idx, item in enumerate(entry["inventory"]):
            if "medicine" not in item or "quantity" not in item:
                raise ValueError(
                    f"Inventory item at PHC index {idx}, item {item_idx} is "
                    f"missing 'medicine' or 'quantity' keys: {item!r}"
                )
            if not isinstance(item["quantity"], (int, float)) or item["quantity"] < 0:
                raise ValueError(
                    f"Inventory item at PHC index {idx}, item {item_idx} has "
                    f"invalid quantity '{item['quantity']}'. "
                    "Must be a non-negative number."
                )
