"""
Statsline Persistence Layer
Supports local JSON/CSV state out-of-the-box with optional Supabase cloud sync.
"""
import json
import os
from typing import List, Dict, Any
from core.underwriting import ArbitrageCandidate

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed_inventory.json")


def load_candidates(filepath: str = DEFAULT_DATA_PATH) -> List[ArbitrageCandidate]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        raw_list = json.load(f)
    return [ArbitrageCandidate(**item) for item in raw_list]


def save_candidates(candidates: List[ArbitrageCandidate], filepath: str = DEFAULT_DATA_PATH) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    payload = [
        {
            "card_id": c.card_id,
            "card_name": c.card_name,
            "category": c.category,
            "raw_cost": c.raw_cost,
            "shipping_cost": c.shipping_cost,
            "grading_fee": c.grading_fee,
            "psa9_comp": c.psa9_comp,
            "psa10_comp": c.psa10_comp,
            "platform_fee_rate": c.platform_fee_rate,
            "is_watermarked_scan": c.is_watermarked_scan,
            "passed_6_gate": c.passed_6_gate,
            "notes": c.notes,
        }
        for c in candidates
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
