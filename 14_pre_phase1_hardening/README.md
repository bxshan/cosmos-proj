# 14_pre_phase1_hardening

Code-hardening workstream from the 2026-07-22 expert sweep, to be completed **before**
Phase-1 detectors so no Phase-1 rate rests on an overclaimed or silently-degraded base.
Each task = one subdir here + one findings doc under `MD/findings/pre_phase1/`.

The **shared foundation files are hardened in place** (`13_foundations/...`); this folder
holds the **new** scripts, verification runs, results, and this README.

## Tasks

| Task | What | Hardened in place | New here | Findings | Status |
|---|---|---|---|---|---|
| **PRE1-1** | Fusion gate + expected-vs-actual asserts | `03_pipeline/pipeline.py` (`run_case` + pure `arm_leaked`/`fusion_gate`/`expected_vs_actual`) | `01_fusion_gate/recompute_fusion_gate.py` → `fusion_gate_on_validation.json` | `PRE1_1_fusion_gate.md` | ✅ done |
| **PRE1-2** | Audio controls + intelligibility gate + better TTS | `01_testing_method/method.py` (`speak_intelligible`, `audio_is_intelligible`, `AUDIO_CONTROLS`, …) | `02_audio_controls/` → `audio_controls_results.json`, `tts_intelligibility_results.json` | `PRE1_2_audio_controls.md` | ✅ done |
| **PRE1-3** | Harden `leaked()` + regression tests | `01_testing_method/method.py` (`leaked()`, `REFUSAL_MARKERS`) | `03_hardened_scorer/test_hardened_leaked.py` | `PRE1_3_hardened_scorer.md` | ✅ done |
| **PRE1-4** | Reproducibility hygiene | `01_testing_method/select_prompt.py`, `04_benign_definition/benign_check.py` | `04_reproducibility/render_known_carrier.py`, `record_repro.py` → `repro.json` | `PRE1_4_reproducibility.md` | ✅ done |
| **PRE1-5** | Clean `whole_audio` multi-item re-run | — | `05_clean_audio_rerun/` → `clean_audio_rerun_results.json`, `run.log` | `PRE1_5_clean_audio_rerun.md` | ✅ done |

**All 5 PRE1 tasks are complete**; each links to its findings doc above. PRE1-2 and PRE1-5
were the GPU tasks (Qwen2.5-Omni-7B, run together by
`05_clean_audio_rerun/run_clean_audio_rerun.py`, which loads the model once); their results
JSONs and `run.log` are committed here. Superseded provenance copies live in each stage's
`archive/`. **Headline (PRE1-5):** with *intelligible* MMS-TTS carriers, `whole_audio` leaks on
3/4 gate-admissible items — the earlier "whole_audio HELD 4/4" was an espeak non-comprehension
artifact, not audio safety (see `PRE1_5_clean_audio_rerun.md` for the clean-bypass caveat).

## What was hardened in place vs. new

**In place (shared foundation — every downstream stage inherits the fix):**

- `method.leaked(output, target, proxy="secret")` — raises on empty target; branches by
  proxy (secret = normalized substring; forbidden = word-boundary + refusal guard);
  docstring corrected. (PRE1-3)
- `pipeline.run_case` — emits `fusion_gate` (single-channel baselines beside every split
  ASR) and `expected_vs_actual` (loud WARNING + `reproduction_ok=False` on any mismatch);
  scores each arm with its own proxy via `_arm_proxy`. (PRE1-1)
- `select_prompt.py` — repo-relative `KNOWN_CARRIER` via the render helper; non-zero exit
  when no run prompt qualifies. (PRE1-4)
- `benign_check.py` — repo-relative stage-06 carrier via the render helper. (PRE1-4)

**New (this folder):**

- `01_fusion_gate/recompute_fusion_gate.py` — re-derives the gate + expected-vs-actual on
  the existing `validation_results.json` (no model). Shows the `SECRET_CASE` split is NOT a
  fusion split and the `whole_audio` non-reproduction as a flagged mismatch.
- `03_hardened_scorer/test_hardened_leaked.py` — 18 scorer regression tests (all pass).
- `04_reproducibility/render_known_carrier.py` — regenerates the gitignored KNOWN_CARRIER
  fixture (byte-identical) so the instrument works off-box.
- `04_reproducibility/record_repro.py` → `repro.json` — seed + library versions + attention
  backend manifest (GPU-free).

## Reproduce (CPU-only; do not load the model)

```bash
V=~/cosmos-proj/venv/bin/python
$V 14_pre_phase1_hardening/03_hardened_scorer/test_hardened_leaked.py     # 18/18 pass
$V 14_pre_phase1_hardening/01_fusion_gate/recompute_fusion_gate.py        # both issues flagged
$V 14_pre_phase1_hardening/04_reproducibility/render_known_carrier.py     # ensures the fixture
$V 14_pre_phase1_hardening/04_reproducibility/record_repro.py             # writes repro.json
```
