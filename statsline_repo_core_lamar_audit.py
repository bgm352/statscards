"""
Lamar 6-Gate Pre-Grading Inspection & OpenCV Vision Engine
Provides both interactive 10x loupe checklist validation and automated OpenCV
centering and surface anomaly detection for raw card scans.
"""
import cv2
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Tuple


@dataclass
class SixGateAudit:
    gate1_front_centering: bool = True      # <= 55/45 L/R and T/B
    gate2_back_centering: bool = True       # <= 70/30 L/R and T/B
    gate3_surface_chromium: bool = True     # Zero print lines, dimples, or roller marks under raking light
    gate4_corners_10x: bool = True          # Zero micro-fraying or flaring under 10x magnification
    gate5_edges_dark_stock: bool = True     # Zero chipping on dark reverse borders (e.g., Bowman Draft / 151)
    gate6_eye_appeal_sleever: bool = True   # No surface hazing, clean penny sleeve & Card Saver I prep
    front_lr_ratio: float = 50.0            # Measured left border % (50.0 = dead center)
    front_tb_ratio: float = 50.0            # Measured top border % (50.0 = dead center)
    inspector_notes: str = ""

    def evaluate(self) -> Dict[str, Any]:
        gates = {
            "Gate 1: Front Centering (<=55/45)": self.gate1_front_centering and (45.0 <= self.front_lr_ratio <= 55.0) and (45.0 <= self.front_tb_ratio <= 55.0),
            "Gate 2: Back Centering (<=70/30)": self.gate2_back_centering,
            "Gate 3: Raking Light Surface / Chromium Check": self.gate3_surface_chromium,
            "Gate 4: 10x Loupe Corner Integrity": self.gate4_corners_10x,
            "Gate 5: Dark-Stock Reverse Edge Check": self.gate5_edges_dark_stock,
            "Gate 6: Sleeve Prep & Zero Hazing": self.gate6_eye_appeal_sleever,
        }
        passed_count = sum(1 for v in gates.values() if v)
        passed_all = passed_count == 6

        return {
            "passed_all": passed_all,
            "gates_passed": f"{passed_count}/6",
            "gate_breakdown": gates,
            "lr_split": f"{self.front_lr_ratio:.1f} / {100 - self.front_lr_ratio:.1f}",
            "tb_split": f"{self.front_tb_ratio:.1f} / {100 - self.front_tb_ratio:.1f}",
            "recommendation": "SHIP TO PSA (Gem 10 Candidate)" if passed_all else "REJECT TO RAW FLIP PILE (Do Not Grade)",
            "notes": self.inspector_notes,
        }


def analyze_card_centering_opencv(
    image_bytes: bytes,
    left_border_px: int,
    right_border_px: int,
    top_border_px: int,
    bottom_border_px: int,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Processes an uploaded card image via OpenCV, overlays centering calibration guides,
    computes high-frequency Laplacian surface variance (to highlight potential scratches/print lines),
    and calculates exact PSA centering splits.
    """
    file_bytes = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes.")

    annotated = img.copy()
    h, w, _ = annotated.shape

    # Draw calibration border lines
    # Left & Right (Cyan)
    cv2.line(annotated, (left_border_px, 0), (left_border_px, h), (255, 255, 0), 2)
    cv2.line(annotated, (w - right_border_px, 0), (w - right_border_px, h), (255, 255, 0), 2)

    # Top & Bottom (Magenta)
    cv2.line(annotated, (0, top_border_px), (w, top_border_px), (255, 0, 255), 2)
    cv2.line(annotated, (0, h - bottom_border_px), (w, h - bottom_border_px), (255, 0, 255), 2)

    total_lr = max(1, left_border_px + right_border_px)
    total_tb = max(1, top_border_px + bottom_border_px)

    lr_left_pct = (left_border_px / total_lr) * 100.0
    lr_right_pct = 100.0 - lr_left_pct

    tb_top_pct = (top_border_px / total_tb) * 100.0
    tb_bottom_pct = 100.0 - tb_top_pct

    max_deviation = max(abs(50.0 - lr_left_pct), abs(50.0 - tb_top_pct))
    if max_deviation <= 5.5:
        psa_centering_grade = "PSA 10 Gem Mint Standard (<= 55/45)"
    elif max_deviation <= 10.0:
        psa_centering_grade = "PSA 9 Mint Standard (<= 60/40)"
    else:
        psa_centering_grade = "PSA 8 or Lower (> 60/40 Off-Center)"

    # Surface edge/scratch density metric via Laplacian variance on inner card region
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    metrics = {
        "lr_ratio": f"{lr_left_pct:.1f} / {lr_right_pct:.1f}",
        "tb_ratio": f"{tb_top_pct:.1f} / {tb_bottom_pct:.1f}",
        "psa_centering_standard": psa_centering_grade,
        "passes_psa10_centering": max_deviation <= 5.5,
        "surface_sharpness_score": round(laplacian_var, 1),
    }

    return cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), metrics
