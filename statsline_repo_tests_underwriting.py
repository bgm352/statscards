"""
Unit tests for Statsline Underwriting & Arbitrage math.
Run with: pytest tests_underwriting.py
"""
from core.underwriting import ArbitrageCandidate, calculate_batch_summary
from core.database import load_candidates


def test_charizard_arbitrage_math():
    zard = ArbitrageCandidate(
        card_id="TEST-ZARD",
        card_name="2023 Pokemon 151 Charizard ex SIR #199",
        category="Core 70% (High-Liquidity)",
        raw_cost=220.0,
        shipping_cost=0.0,
        grading_fee=40.0,
        psa9_comp=345.0,
        psa10_comp=1200.0,
        platform_fee_rate=0.13,
    )
    assert zard.all_in_basis == 260.00
    assert zard.net_psa10_proceeds == 1044.00
    assert zard.psa10_net_profit == 784.00
    assert zard.evaluate_deal()["verdict"] == "MASTER ARBITRAGE LOCK"


def test_curry_comc_rejection():
    curry_comc = ArbitrageCandidate(
        card_id="TEST-COMC",
        card_name="2018-19 Prizm Silver Stephen Curry #222 (COMC)",
        category="Core 70% (High-Liquidity)",
        raw_cost=52.28,
        shipping_cost=0.0,
        grading_fee=40.0,
        psa9_comp=95.0,
        psa10_comp=385.0,
        is_watermarked_scan=True,
        passed_6_gate=False,
    )
    res = curry_comc.evaluate_deal()
    assert res["verdict"] == "HARD PASS"


def test_master_batch_seed_totals():
    candidates = load_candidates()
    summary = calculate_batch_summary(candidates, hours_invested=2.5, w2_hourly_benchmark=70.0)
    assert summary["card_count"] == 4
    assert abs(summary["total_basis"] - 508.10) < 0.05
    assert summary["all_gem_profit"] > 1300.0
