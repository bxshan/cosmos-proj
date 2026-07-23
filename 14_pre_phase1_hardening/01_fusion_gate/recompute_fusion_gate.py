"""PRE1-1 -- recompute the fusion gate + expected-vs-actual on the EXISTING
validation_results.json, with NO model (derived purely from the stored verdicts).

Demonstrates the two hardening checks on already-collected data:
  (a) the SECRET_CASE `split` is NOT a genuine fusion split -- `audio_alone` alone
      leaks 4/4, so a single channel fully explains the split (is_fusion_split=False);
  (b) `whole_audio` expected=VIOLATED but actual=HELD is flagged as a mismatch
      (reproduction_ok=False) -- the non-reproduction the old harness passed silently.

Reuses the SAME pure functions the hardened pipeline.run_case now uses
(pipeline.fusion_gate / pipeline.expected_vs_actual), so this offline re-derivation
and the live run share one implementation. CPU-only.
"""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_REPO, "13_foundations", "03_pipeline"))

import pipeline  # noqa: E402  (fusion_gate, expected_vs_actual -- pure, model-free)

VAL_JSON = os.path.join(_REPO, "13_foundations", "03_pipeline", "validation_results.json")
OUT_JSON = os.path.join(_HERE, "fusion_gate_on_validation.json")


def main():
    with open(VAL_JSON) as f:
        val = json.load(f)
    pc = val["per_condition"]

    # Reconstruct the case.expected dict from the per-arm "expected" fields the
    # pipeline stored (it never checked them -- that is the silent-pass bug).
    expected = {arm: rec.get("expected") for arm, rec in pc.items() if rec.get("expected")}

    fg = pipeline.fusion_gate(pc)
    eva = pipeline.expected_vs_actual(pc, expected)

    print(f"=== fusion gate on {os.path.basename(VAL_JSON)} (case={val['case']}) ===",
          flush=True)
    print(f"  split_asr={fg['split_asr']}  image_alone_asr={fg['image_alone_asr']}  "
          f"audio_alone_asr={fg['audio_alone_asr']}", flush=True)
    print(f"  split_leaked={fg['split_leaked']}  image_alone_held={fg['image_alone_held']}  "
          f"audio_alone_held={fg['audio_alone_held']}", flush=True)
    print(f"  is_fusion_split={fg['is_fusion_split']}  "
          f"(expected False: audio_alone alone already leaks)", flush=True)

    print("\n=== expected-vs-actual ===", flush=True)
    for arm, c in eva["checks"].items():
        tag = "OK  " if c["match"] else "MISMATCH"
        print(f"  {tag} {arm:14s} expected={c['expected']:9s} actual={c['actual']}", flush=True)
    if not eva["reproduction_ok"]:
        print("!" * 64, flush=True)
        print("WARNING: reproduction_ok=False -- expected-vs-actual mismatch(es):", flush=True)
        for m in eva["mismatches"]:
            print(f"    MISMATCH arm={m['arm']} expected={m['expected']} actual={m['actual']}",
                  flush=True)
        print("!" * 64, flush=True)

    out = {
        "source": VAL_JSON,
        "case": val["case"],
        "expected_reconstructed": expected,
        "fusion_gate": fg,
        "expected_vs_actual": eva,
        "reproduction_ok": eva["reproduction_ok"],
        "demonstrates": {
            "a_split_is_not_fusion": (fg["is_fusion_split"] is False
                                      and fg["audio_alone_held"] is False),
            "b_whole_audio_mismatch_flagged": any(
                m["arm"] == "whole_audio" for m in eva["mismatches"]),
        },
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWROTE {OUT_JSON}", flush=True)
    print(f"DEMONSTRATES: (a) split-not-fusion={out['demonstrates']['a_split_is_not_fusion']}  "
          f"(b) whole_audio-mismatch-flagged={out['demonstrates']['b_whole_audio_mismatch_flagged']}",
          flush=True)


if __name__ == "__main__":
    main()
