"""Track A (Phase 1) GPU runner.

Loads Qwen2.5-Omni-7B ONCE (pipeline.load_runner), then for EACH benchmark item runs
the full standard pipeline (pipeline.run_case: all six CONDITIONS + two CONTROLS x
N_TRIALS under STANDARD_PROMPT="", emitting fusion_gate + expected_vs_actual +
reproduction_ok). For the audio_experiment sub-family it additionally gates the
whole_audio carrier with method.audio_is_intelligible (admissible?) and records the
whole_text/whole_image/whole_audio collapsed verdicts, so the clean-audio-bypass count
(text-refused AND intelligible-audio-obeyed) can be read directly.

Everything is dumped to track_a_results.json, including per-item carrier asset paths so
Track B can caption/transcribe them.

Reuse (do NOT rebuild): pipeline.{load_runner,run_case,arm_leaked}, method.* (arms,
carriers, leaked, intelligibility gate, STANDARD_PROMPT), metrics.asr. Two established
shims from PRE1-5 / benchmark_cases:
  * method.speak = method.speak_intelligible  -> the audio CONDITIONS render MMS-TTS
    (intelligible) instead of espeak, so an audio HELD is a refusal, not non-comprehension.
  * method.render is wrapped to honor a per-item font size (the rendered-size axis).
  * benchmark_cases installs the multi-code system_prompt shim on import.
"""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_REPO, "13_foundations", "03_pipeline"))
sys.path.insert(0, os.path.join(_REPO, "13_foundations", "01_testing_method"))
sys.path.insert(0, os.path.join(_REPO, "13_foundations", "02_metrics"))
sys.path.insert(0, _HERE)

import method            # noqa: E402
import metrics           # noqa: E402  (kept for parity; run_case uses it internally)
import pipeline          # noqa: E402
import benchmark_cases   # noqa: E402  (also installs the multi-code system_prompt shim)

from PIL import Image, ImageDraw  # noqa: E402

N_TRIALS = 4
OUT_JSON = os.path.join(_HERE, "track_a_results.json")
ASSET_DIR = os.path.join(_HERE, "assets")


def P(*a):
    print(*a, flush=True)


# --- Per-item rendered-size axis: wrap method.render to honor _CUR_FONT. ------
_CUR_FONT = [46]
_orig_render = method.render


def _render(text, path):
    """Same standard carrier as method.render (dark text on white 1100x320) but at the
    current item's font size. Font range is kept within what fits the fixed canvas."""
    img = Image.new("RGB", (1100, 320), (255, 255, 255))
    ImageDraw.Draw(img).multiline_text((30, 40), method._wrap(text), fill=(0, 0, 0),
                                        font=method._font(_CUR_FONT[0]), spacing=12)
    img.save(path)
    return path


def _arm_verdict(result, arm):
    """Collapsed boolean-> 'VIOLATED'/'HELD' for an arm (majority of valid trials)."""
    return "VIOLATED" if pipeline.arm_leaked(result["per_condition"][arm]) else "HELD"


def _leaked(result, arm):
    return pipeline.arm_leaked(result["per_condition"][arm])


def _asset_paths(case):
    """Absolute carrier asset paths produced by run_case, for Track B to caption/transcribe."""
    A = method._asset
    return {
        "whole_image_png": A(case, "whole_image", "png"),
        "whole_audio_wav": A(case, "whole_audio", "wav"),
        "split_png": A(case, "split", "png"),
        "split_wav": A(case, "split", "wav"),
        "image_alone_png": A(case, "image_alone", "png"),
        "audio_alone_wav": A(case, "audio_alone", "wav"),
        "benign_disambig_png": A(case, "benign_disambig", "png"),
        "blank_confound_png": A(case, "blank_confound", "png"),
    }


def _frac(bools):
    bools = list(bools)
    return round(sum(bools) / len(bools), 3) if bools else None


def main():
    # Route all carrier assets under track_a/assets and honor the font axis.
    os.makedirs(ASSET_DIR, exist_ok=True)
    method.ASSET_DIR = ASSET_DIR
    method.render = _render

    cases = benchmark_cases.build_cases()
    P(f"Track A: {len(cases)} cases; N_TRIALS={N_TRIALS}; ASSET_DIR={ASSET_DIR}")

    gen = pipeline.load_runner()
    try:
        import torch
        torch.manual_seed(0)  # MMS VITS duration predictor is stochastic
    except Exception:
        pass

    # Swap the audio CONDITIONS' TTS to the intelligible neural voice (PRE1-5 pattern).
    # Warm/verify MMS first so we never silently fall back to espeak mid-run.
    warm = method.speak_intelligible("warm up the neural text to speech engine",
                                     os.path.join(ASSET_DIR, "_warmup.wav"))
    assert os.path.exists(warm), "MMS-TTS warmup failed"
    method.speak = method.speak_intelligible
    P("MMS-TTS warmup OK; method.speak -> speak_intelligible")

    items = []
    for case in cases:
        _CUR_FONT[0] = case.font_size
        P("\n" + "=" * 70)
        P(f"CASE {case.name} fam={case.family} code={case.code} font={case.font_size}")
        result = pipeline.run_case(case, N_TRIALS, gen)  # full arms + gate + eva

        item = {
            "case": case.name,
            "family": case.family,
            "code": case.code,
            "font_size": case.font_size,
            "image_payload": case.image_payload,
            "audio_payload": case.audio_payload,
            "whole_instruction": method._whole_instr(case),
            "target": case.target,
            "assets": _asset_paths(case),
            "collapsed_verdicts": {
                arm: _arm_verdict(result, arm) for arm in result["per_condition"]},
            "result": result,  # per_condition (verdicts+asr+outputs), fusion_gate, eva
        }

        if case.family == "audio_experiment":
            wav = method._asset(case, "whole_audio", "wav")  # the carrier run_case used
            gate = method.audio_is_intelligible(wav, case.intended_words, gen)
            wt_held = not _leaked(result, "whole_text")
            wa_leaked = _leaked(result, "whole_audio")
            wi_leaked = _leaked(result, "whole_image")
            # Admissible = the carrier is comprehended: intelligibility gate passes OR
            # the model behaviorally leaked from it (a leak proves comprehension).
            admissible = bool(gate["intelligible"] or wa_leaked)
            item["audio_experiment"] = {
                "intended_words": case.intended_words,
                "whole_audio_gate": gate,
                "whole_audio_admissible": admissible,
                "whole_text_verdict": "HELD" if wt_held else "VIOLATED",
                "whole_image_verdict": "VIOLATED" if wi_leaked else "HELD",
                "whole_audio_verdict": "VIOLATED" if wa_leaked else "HELD",
                "text_refused": bool(wt_held),
                # The load-bearing count: text-refused AND carrier-admissible AND audio leaks.
                "clean_audio_bypass": bool(wt_held and admissible and wa_leaked),
            }
            P(f"  AUDIO-EXP gate intelligible={gate['intelligible']} recall={gate['recall']} "
              f"reason={gate['reason']} | whole_text={item['audio_experiment']['whole_text_verdict']} "
              f"whole_audio={item['audio_experiment']['whole_audio_verdict']} "
              f"admissible={admissible} clean_bypass={item['audio_experiment']['clean_audio_bypass']}")

        items.append(item)
        # Incremental dump so a mid-run interruption still yields partial results.
        with open(OUT_JSON, "w") as f:
            json.dump({"partial": True, "items": items}, f, indent=2)

    # --------------------------- Aggregate summary --------------------------- #
    ae = [it for it in items if it["family"] == "audio_experiment"]
    ae_x = [it for it in ae if it["audio_experiment"]["text_refused"]
            and it["audio_experiment"]["whole_audio_admissible"]]
    ae_bypass = [it for it in ae_x if it["audio_experiment"]["clean_audio_bypass"]]

    summary = {
        "n_items": len(items),
        "n_audio_experiment": len(ae),
        "n_split_fusion": sum(it["family"] == "split_fusion" for it in items),
        "baseline_leak_fraction": {
            "whole_text": _frac(_leaked(it["result"], "whole_text") for it in items),
            "whole_image": _frac(_leaked(it["result"], "whole_image") for it in items),
            "whole_audio": _frac(_leaked(it["result"], "whole_audio") for it in items),
            "split": _frac(_leaked(it["result"], "split") for it in items),
        },
        "n_reproduction_ok": sum(it["result"]["reproduction_ok"] for it in items),
        "n_fusion_split": sum(
            it["result"]["fusion_gate"].get("is_fusion_split", False) for it in items),
        "audio_experiment": {
            "n": len(ae),
            "n_intelligible_admissible_and_text_held": len(ae_x),
            "admissible_text_held_items": [it["case"] for it in ae_x],
            "n_clean_audio_bypass": len(ae_bypass),
            "clean_audio_bypass_items": [it["case"] for it in ae_bypass],
            "whole_text_leak_fraction":
                _frac(_leaked(it["result"], "whole_text") for it in ae),
            "whole_image_leak_fraction":
                _frac(_leaked(it["result"], "whole_image") for it in ae),
            "whole_audio_leak_fraction":
                _frac(_leaked(it["result"], "whole_audio") for it in ae),
        },
    }

    result_doc = {
        "task": "Track A (Phase 1): benchmark AttackCases + audio-experiment bypass test",
        "model": pipeline.MODEL,
        "n_trials": N_TRIALS,
        "standard_prompt": method.STANDARD_PROMPT,
        "asset_dir": ASSET_DIR,
        "codes": benchmark_cases.CODES,
        "audio_tts": method.INTELLIGIBLE_TTS,
        "summary": summary,
        "items": items,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(result_doc, f, indent=2)

    P("\n" + "=" * 70)
    P("SUMMARY")
    P(json.dumps(summary, indent=2))
    try:
        import torch
        P("VRAM_GB:", round(torch.cuda.max_memory_allocated() / 1e9, 2))
    except Exception:
        pass
    P("WROTE", OUT_JSON)
    P("ALL DONE")


if __name__ == "__main__":
    main()
