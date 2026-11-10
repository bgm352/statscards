# 💎 Statsline: Dealer Arbitrage & Lamar 6-Gate Inspection Engine

A Python, OpenCV, and Streamlit underwriting application built to manage high-conviction, low-volume sports card and TCG dealer arbitrage batches.

## 🚀 Core Features

1. **Master Batch Financial Ledger (`core/underwriting.py`)**
   - Tracks acquisition basis, PSA grading tiers, platform fee deductions (`~13%`), **PSA 9 Downside Floor protection**, **Realistic Hybrid outcomes**, and **All-Gem PSA 10 ceilings**.
   - Benchmarks batch profit against active hourly labor (`$/hr` yield vs. W-2 hourly rate).
   - Pre-seeded with the 4-Card Master Batch (**2023 Bowman Draft Paul Skenes Refractor**, **2025 Bowman Chrome Jac Caglianone Gold Shimmer `/50`**, **2024 Bowman Draft Nick Kurtz 1st Refractor**, and **2023 Pokémon 151 Charizard ex SIR `#199`**) plus evaluated rejections (**2018-19 Prizm Silver Stephen Curry `#222`** COMC/eBay listings and **2024-25 Prizm Base `#134`**).

2. **Live Listing Underwriter & Max Safe Bid Calculator**
   - Enforces the **2x / 3x Multiplier Rule** and automatically calculates the **Maximum Safe Raw Bid** so a PSA 9 grade still covers all-in basis.
   - Automatically flags watermarked consignment scans (e.g., COMC) that obscure surface hairlines on chromium stock.

3. **Lamar 6-Gate Inspection Desk & OpenCV Vision Analyzer (`core/lamar_audit.py`)**
   - Interactive 6-Gate 10x loupe and raking-light checklist.
   - OpenCV border calibration tool that overlays digital centering guides, computes exact Left/Right and Top/Bottom ratios against PSA 10 (`<= 55/45`) standards, and calculates Laplacian surface variance.

4. **10-Card Monthly Scaling Blueprint**
   - Simulates scaling to a continuous 10-card monthly pipeline using the **70/30 Portfolio Rule** (70% Floor-Protected Core, 30% Asymmetric Lottery Parallels) and calculatesPSA turnaround windows to hit peak February/March Spring Training liquidity.

## 🛠️ Quickstart

```bash
pip install -r requirements.txt
pytest tests_underwriting.py
streamlit run app.py
```
