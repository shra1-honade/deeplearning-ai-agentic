"""Inventory & transactions backend for the M5 "Customer Service Agent" lab.

Coursera's platform ships this module alongside the notebook, but it wasn't
downloaded locally. Reconstructed from the notebook's own markdown spec
(field names/types, and the exact SG001/SG005/opening-balance values it
asserts later in the narrative).
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

_INVENTORY_SEED = [
    {
        "item_id": "SG001",
        "name": "Aviator",
        "description": "Timeless teardrop lenses in a thin metal frame, a classic pilot-inspired silhouette.",
        "quantity_in_stock": 23,
        "price": 80.0,
    },
    {
        "item_id": "SG002",
        "name": "Wayfarer",
        "description": "Bold trapezoidal acetate frame with a flat top, a versatile everyday staple.",
        "quantity_in_stock": 15,
        "price": 70.0,
    },
    {
        "item_id": "SG003",
        "name": "Cat-Eye",
        "description": "Upswept outer corners in a glossy acetate frame, a retro-glam statement piece.",
        "quantity_in_stock": 12,
        "price": 95.0,
    },
    {
        "item_id": "SG004",
        "name": "Moon",
        "description": "Oversized round silhouette in brushed metal, a bold retro-inspired shape.",
        "quantity_in_stock": 8,
        "price": 120.0,
    },
    {
        "item_id": "SG005",
        "name": "Classic",
        "description": (
            "Classic round profile with minimalist metal frames, offering a timeless "
            "and versatile style that fits both casual and formal wear."
        ),
        "quantity_in_stock": 10,
        "price": 60.0,
    },
]

_OPENING_BALANCE = 500.00


def create_inventory() -> list[dict]:
    """Return a fresh copy of the sunglasses inventory seed."""
    return deepcopy(_INVENTORY_SEED)


def create_transactions() -> list[dict]:
    """Return a fresh single-row transaction log with the opening balance."""
    return [
        {
            "transaction_id": "TXN001",
            "customer_name": "OPENING_BALANCE",
            "transaction_summary": "Opening balance",
            "transaction_amount": _OPENING_BALANCE,
            "balance_after_transaction": _OPENING_BALANCE,
            "timestamp": datetime.now().isoformat(),
        }
    ]


def seed_db():
    """Build a fresh in-memory TinyDB store and seed both tables.

    Returns (db, inventory_tbl, transactions_tbl).
    """
    db = TinyDB(storage=MemoryStorage)
    inventory_tbl = db.table("inventory")
    transactions_tbl = db.table("transactions")

    inventory_tbl.truncate()
    transactions_tbl.truncate()
    inventory_tbl.insert_multiple(create_inventory())
    transactions_tbl.insert_multiple(create_transactions())

    return db, inventory_tbl, transactions_tbl


def build_schema_block(inventory_tbl, transactions_tbl) -> str:
    """Text block describing both tables' fields plus a couple of sample rows."""
    inv_sample = inventory_tbl.all()[:2]
    txn_sample = transactions_tbl.all()[:2]

    return f"""Table: inventory_tbl
Fields: item_id (str), name (str), description (str), quantity_in_stock (int), price (float)
Sample rows:
{json.dumps(inv_sample, indent=2)}

Table: transactions_tbl
Fields: transaction_id (str), customer_name (str), transaction_summary (str), transaction_amount (float), balance_after_transaction (float), timestamp (str, ISO-8601)
Sample rows:
{json.dumps(txn_sample, indent=2)}
"""


def get_current_balance(tbl) -> float:
    """Balance after the most recently inserted transaction (0.0 if empty)."""
    rows = tbl.all()
    if not rows:
        return 0.0
    return rows[-1]["balance_after_transaction"]


def next_transaction_id(tbl, prefix: str = "TXN") -> str:
    """Next sequential transaction id with the given prefix, e.g. TXN002."""
    nums = []
    for row in tbl.all():
        tid = row.get("transaction_id", "")
        if tid.startswith(prefix) and tid[len(prefix):].isdigit():
            nums.append(int(tid[len(prefix):]))
    next_num = max(nums, default=0) + 1
    return f"{prefix}{next_num:03d}"
