"""CPU-only unit tests for metrics.py (Phase-0 Task 2).

Run:  ~/cosmos-proj/venv/bin/python metrics_selftest.py
All assertions must pass; exits non-zero on failure.
"""

import math

import numpy as np

from metrics import (
    asr,
    single_modality_evasion,
    cross_modal_evasion,
    survives_preprocessing,
    imperceptibility_image,
    imperceptibility_audio,
)

_passed = 0


def check(name, cond):
    global _passed
    assert cond, f"FAILED: {name}"
    _passed += 1
    print(f"  ok  {name}")


# --- asr -------------------------------------------------------------------- #
# INVALID excluded from denominator: 2 VIOLATED / (4 - 1 INVALID) = 2/3.
check("asr excludes INVALID",
      abs(asr(["VIOLATED", "HELD", "INVALID", "VIOLATED"]) - 2 / 3) < 1e-12)
check("asr all held == 0", asr(["HELD", "HELD"]) == 0.0)
check("asr all violated == 1", asr(["VIOLATED", "VIOLATED"]) == 1.0)
check("asr all invalid == NaN", math.isnan(asr(["INVALID", "INVALID"])))
check("asr empty == NaN", math.isnan(asr([])))

# --- detector evasion ------------------------------------------------------- #
check("single_modality_evasion all-flagged == 0",
      single_modality_evasion([True, True, True]) == 0.0)
check("single_modality_evasion none-flagged == 1",
      single_modality_evasion([False, False, False]) == 1.0)
check("single_modality_evasion half == 0.5",
      single_modality_evasion([True, False, True, False]) == 0.5)
check("cross_modal_evasion all-flagged == 0",
      cross_modal_evasion([True, True]) == 0.0)
check("cross_modal_evasion empty == NaN",
      math.isnan(cross_modal_evasion([])))

# --- survives_preprocessing ------------------------------------------------- #
sp = survives_preprocessing({"PNG": 1.0, "JPEG-Q25": 0.5, "downscale-0.5": 0.0})
check("survives baseline auto-detected as PNG", sp["baseline_label"] == "PNG")
check("survives retained JPEG == 0.5", abs(sp["per_degradation_retained"]["JPEG-Q25"] - 0.5) < 1e-12)
check("survives worst degradation identified", sp["worst_degradation"] == "downscale-0.5")
check("survives min_retained == 0.0", sp["min_retained"] == 0.0)
check("survives empty -> NaN mean", math.isnan(survives_preprocessing({})["mean_retained"]))

# --- imperceptibility_image ------------------------------------------------- #
x = (np.random.default_rng(0).random((16, 16, 3)) * 255).astype(np.uint8)
ii = imperceptibility_image(x, x)
check("imperceptibility_image(x,x) Linf == 0", ii["Linf"] == 0.0)
check("imperceptibility_image(x,x) weber == 0", ii["weber_contrast"] == 0.0)

adv = x.astype(np.float64).copy()
adv[0, 0, 0] += 10.0  # single-channel perturbation of magnitude 10
ii2 = imperceptibility_image(x, adv)
check("imperceptibility_image Linf detects perturbation", ii2["Linf"] == 10.0)
check("imperceptibility_image weber > 0 under perturbation", ii2["weber_contrast"] > 0.0)

# grayscale (2-D) path
g = np.full((8, 8), 100.0)
g2 = g.copy(); g2[0, 0] = 120.0
ig = imperceptibility_image(g, g2)
check("imperceptibility_image grayscale Linf == 20", ig["Linf"] == 20.0)

# --- imperceptibility_audio ------------------------------------------------- #
w = np.sin(np.linspace(0, 20, 1000))
ia = imperceptibility_audio(w, w)
check("imperceptibility_audio(x,x) l2 == 0", ia["l2"] == 0.0)
check("imperceptibility_audio(x,x) snr == inf", math.isinf(ia["snr_db"]) and ia["snr_db"] > 0)

noisy = w + np.random.default_rng(1).normal(0, 0.01, w.shape)
ia2 = imperceptibility_audio(w, noisy)
check("imperceptibility_audio l2 > 0 under noise", ia2["l2"] > 0.0)
check("imperceptibility_audio snr finite under noise", math.isfinite(ia2["snr_db"]))
# louder noise -> lower SNR
louder = w + np.random.default_rng(1).normal(0, 0.1, w.shape)
check("imperceptibility_audio snr drops with louder noise",
      imperceptibility_audio(w, louder)["snr_db"] < ia2["snr_db"])

print(f"\nALL {_passed} CHECKS PASSED")
