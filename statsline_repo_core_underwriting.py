"""
Statsline Underwriting & Arbitrage Engine
Implements the 2x/3x Rule, PSA 9 Downside Floor Protection, and Hourly Yield ROI models.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class ArbitrageCandidate:
    card_id: str
    card_name: str
    category: str  # e.g., "Core 70% (High-Liquidity)" or "Lottery 30% (Asymmetric)"
    raw_cost: float
    shipping_cost: float
    grading_fee: float
    psa9_comp: float
    psa10_comp: float
    platform_fee_rate: float = 0.13
    is_watermarked_scan: bool = False
    passed_6_gate: bool = True
    notes: str = ""

    @property
    def all_in_basis(self) -> float:
        return round(self.raw_cost + self.shipping_cost + self.grading_fee, 2)

    @property
    def net_psa9_proceeds(self) -> float:
        return round(self.psa9_comp * (1.0 - self.platform_fee_rate), 2)

    @property
    def net_psa10_proceeds(self) -> float:
        return round(self.psa10_comp * (1.0 - self.platform_fee_rate), 2)

    @property
    def psa9_net_profit(self) -> float:
        return round(self.net_psa9_proceeds - self.all_in_basis, 2)

    @property
    def psa10_net_profit(self) -> float:
        return round(self.net_psa10_proceeds - self.all_in_basis, 2)

    @property
    def cash_multiplier(self) -> float:
        if self.all_in_basis <= 0:
            return 0.0
        return round(self.net_psa10_proceeds / self.all_in_basis, 2)

    @property
    def gross_multiplier(self) -> float:
        if self.all_in_basis <= 0:
            return 0.0
        return round(self.psa10_comp / self.all_in_basis, 2)

    def max_raw_bid_for_floor_protection(self) -> float:
        """
        Calculates the maximum raw purchase price (including shipping) so that 
        a PSA 9 grade still breaks even after platform fees and grading costs.
        """
        max_basis = self.net_psa9_proceeds
        return round(max(0.0, max_basis - self.grading_fee), 2)

    def evaluate_deal(self) -> Dict[str, Any]:
        """
        Runs the candidate through the Statsline Dealer Arbitrage underwriting gates:
        1. 2x / 3x Multiplier Rule
        2. PSA 9 Floor Protection Check
        3. Scan / Condition Integrity Filter
        """
        passes_2x = self.gross_multiplier >= 2.0
        passes_3x = self.gross_multiplier >= 3.0
        floor_protected = self.psa9_comp >= (self.all_in_basis * 0.95)  # Within 5% of raw+grading basis
        strict_floor_net = self.psa9_net_profit >= -5.0  # Max $5 haircut after fees

        reasons = []
        if self.is_watermarked_scan:
            reasons.append("FAIL: Watermarked stock scan (e.g., COMC) masks chromium surface flaws/centering.")
        if not self.passed_6_gate:
            reasons.append("FAIL: Rejected at Lamar 6-Gate physical loupe audit.")
        if not passes_2x:
            reasons.append(f"FAIL: Gross multiplier ({self.gross_multiplier}x) fails minimum 2.0x rule.")
        if self.psa10_net_profit < 35.0:
            reasons.append(f"FAIL: Narrow spread (+${self.psa10_net_profit}) does not justify grading queue lockup.")
        if not floor_protected:
            max_bid = self.max_raw_bid_for_floor_protection()
            reasons.append(
                f"WARNING: PSA 9 Trap (${self.psa9_comp} comp vs ${self.all_in_basis} basis). "
                f"Target raw buy-in <= ${max_bid:.2f} shipped to lock floor."
            )

        if self.is_watermarked_scan or not self.passed_6_gate or not passes_2x or self.psa10_net_profit < 35.0:
            verdict = "HARD PASS"
        elif not floor_protected:
            verdict = "HIGH CONVICTION ONLY (Floor Exposed)"
        elif passes_3x and strict_floor_net:
            verdict = "MASTER ARBITRAGE LOCK"
        else:
            verdict = "APPROVED"

        return {
            **asdict(self),
            "all_in_basis": self.all_in_basis,
            "net_psa9_proceeds": self.net_psa9_proceeds,
            "net_psa10_proceeds": self.net_psa10_proceeds,
            "psa9_net_profit": self.psa9_net_profit,
            "psa10_net_profit": self.psa10_net_profit,
            "cash_multiplier": self.cash_multiplier,
            "gross_multiplier": self.gross_multiplier,
            "max_safe_raw_bid": self.max_raw_bid_for_floor_protection(),
            "verdict": verdict,
            "flags": reasons if reasons else ["All underwriting gates cleared."],
        }


def calculate_batch_summary(
    candidates: List[ArbitrageCandidate],
    hours_invested: float = 2.5,
    w2_hourly_benchmark: float = 70.0,
) -> Dict[str, Any]:
    """
    Computes Master Batch financial totals, realistic hybrid outcome (75% Gem / 25% Mint),
    and Hourly Yield ROI vs active W-2 labor.
    """
    active = [c for c in candidates if c.passed_6_gate and not c.is_watermarked_scan]
    if not active:
        return {}

    total_raw = sum(c.raw_cost + c.shipping_cost for c in active)
    total_grading = sum(c.grading_fee for c in active)
    total_basis = sum(c.all_in_basis for c in active)

    all_gem_gross = sum(c.psa10_comp for c in active)
    all_gem_net = sum(c.net_psa10_proceeds for c in active)
    all_gem_profit = round(all_gem_net - total_basis, 2)

    all_9_gross = sum(c.psa9_comp for c in active)
    all_9_net = sum(c.net_psa9_proceeds for c in active)
    all_9_profit = round(all_9_net - total_basis, 2)

    # Realistic Mixed Model: Sort by lowest profit to simulate lowest 1-2 cards grading PSA 9
    sorted_by_spread = sorted(active, key=lambda x: x.psa10_net_profit)
    realistic_net = 0.0
    for idx, card in enumerate(sorted_by_spread):
        # Lowest margin card(s) take PSA 9 in realistic model (~25% of batch)
        num_nines = max(1, len(active) // 4)
        if idx < num_nines:
            realistic_net += card.net_psa9_proceeds
        else:
            realistic_net += card.net_psa10_proceeds

    realistic_profit = round(realistic_net - total_basis, 2)
    effective_hourly_all_gem = round(all_gem_profit / hours_invested, 2) if hours_invested > 0 else 0.0
    effective_hourly_realistic = round(realistic_profit / hours_invested, 2) if hours_invested > 0 else 0.0
    w2_equivalent_hours = round(all_gem_profit / w2_hourly_benchmark, 1) if w2_hourly_benchmark > 0 else 0.0

    return {
        "card_count": len(active),
        "total_raw_spend": round(total_raw, 2),
        "total_grading_spend": round(total_grading, 2),
        "total_basis": round(total_basis, 2),
        "all_gem_gross": round(all_gem_gross, 2),
        "all_gem_net": round(all_gem_net, 2),
        "all_gem_profit": all_gem_profit,
        "portfolio_multiplier": round(all_gem_net / total_basis, 2) if total_basis > 0 else 0.0,
        "all_9_gross": round(all_9_gross, 2),
        "all_9_net": round(all_9_net, 2),
        "all_9_profit": all_9_profit,
        "realistic_net": round(realistic_net, 2),
        "realistic_profit": realistic_profit,
        "hours_invested": hours_invested,
        "effective_hourly_all_gem": effective_hourly_all_gem,
        "effective_hourly_realistic": effective_hourly_realistic,
        "w2_equivalent_hours": w2_equivalent_hours,
    }
