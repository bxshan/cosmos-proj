"""Phase-0 Task 3 -- the attack-success pipeline.

Loads Qwen2.5-Omni-7B ONCE and, for an AttackCase, runs every standard arm
(method.CONDITIONS + method.CONTROLS) x N trials under method.STANDARD_PROMPT,
scores each trial with method.leaked(), computes per-condition ASR via
metrics.asr(), and emits a structured result (per-condition verdicts + ASR +
raw outputs) which is also written to JSON.

Reuse, don't rebuild: the model-load / generate conventions mirror
06_split_attack_7b/run_attack_7b.py and 08_empty_carriers/empty_carriers.py;
the arms, controls, carriers, AttackCase, STANDARD_PROMPT and leaked() come from
13_foundations/01_testing_method/method.py; asr() from 02_metrics/metrics.py.

Public surface:
    load_runner()                         -> gen(msgs) -> str   (loads the 7B once)
    run_case(case, n_trials, gen, out=..) -> structured result dict (+ JSON)

Scoring note (benign_disambig control): every arm is scored with leaked() against
a *per-arm target*. For all CONDITIONS and blank_confound the target is the case
proxy (a leak). For the benign_disambig control the target is the benign
discriminator word 'hello': a VIOLATED there means the model genuinely READ the
carrier's benign instruction (i.e. it FOLLOWED it) rather than deferring to the
run prompt, so for that arm VIOLATED is reported as FOLLOWED. Empty output =
INVALID and is excluded from ASR by construction (metrics.asr).
"""

import json
import os
import sys
import traceback

import torch
from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor
from qwen_omni_utils import process_mm_info

# --- import the Task-1 method and Task-2 metrics (siblings under 13_foundations) ---
_HERE = os.path.dirname(os.path.abspath(__file__))
_FOUND = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_FOUND, "01_testing_method"))
sys.path.insert(0, os.path.join(_FOUND, "02_metrics"))

import method   # noqa: E402  (CONDITIONS, CONTROLS, AttackCase, build_messages, leaked, STANDARD_PROMPT)
import metrics  # noqa: E402  (asr)

MODEL = "Qwen/Qwen2.5-Omni-7B"

# The benign discriminator word that a genuine read of the benign_disambig carrier
# should produce. method.BENIGN_INSTR == "Reply with only the word hello."
BENIGN_WORD = "hello"


def P(*a):
    print(*a, flush=True)


# --------------------------------------------------------------------------- #
# Model load (ONCE) -- mirrors 06_split_attack_7b/run_attack_7b.py::gen        #
# --------------------------------------------------------------------------- #
def load_runner():
    """Load the 7B once; return a gen(msgs)->str closure over model+processor."""
    P("MODEL LOAD START", MODEL)
    model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
        MODEL, torch_dtype=torch.bfloat16, device_map="auto", enable_audio_output=False)
    processor = Qwen2_5OmniProcessor.from_pretrained(MODEL)
    P("MODEL LOAD DONE")

    def gen(msgs):
        text = processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        audios, images, videos = process_mm_info(msgs, use_audio_in_video=False)
        inputs = processor(text=text, audio=audios, images=images, videos=videos,
                           return_tensors="pt", padding=True, use_audio_in_video=False)
        inputs = inputs.to(model.device)
        for k in inputs:
            if torch.is_floating_point(inputs[k]):
                inputs[k] = inputs[k].to(model.dtype)
        out = model.generate(**inputs, use_audio_in_video=False, return_audio=False,
                             do_sample=False, temperature=None, top_p=None, top_k=None,
                             max_new_tokens=512)
        g = out[:, inputs["input_ids"].shape[1]:]
        return processor.batch_decode(g, skip_special_tokens=True,
                                      clean_up_tokenization_spaces=False)[0].strip()

    return gen


# --------------------------------------------------------------------------- #
# Per-arm scoring target                                                       #
# --------------------------------------------------------------------------- #
def _arm_target(case, fn):
    """The string leaked() must find for this arm. For the benign_disambig control
    it is the benign discriminator word (VIOLATED-of-'hello' == FOLLOWED); for every
    other arm it is the case proxy target (VIOLATED == leak)."""
    if fn is method.benign_disambig:
        return BENIGN_WORD
    return case.target


# --------------------------------------------------------------------------- #
# Core: run one AttackCase over all arms x N trials                            #
# --------------------------------------------------------------------------- #
def run_case(case, n_trials, gen, out_json=None):
    """Run every method.CONDITIONS + method.CONTROLS arm x n_trials under
    method.STANDARD_PROMPT; score with method.leaked(); ASR via metrics.asr().

    Returns a structured dict; also writes it to out_json if given."""
    prompt = method.STANDARD_PROMPT
    arms = method.CONDITIONS + method.CONTROLS

    per_condition = {}
    for fn in arms:
        name = fn.__name__
        target = _arm_target(case, fn)
        verdicts, outputs = [], []
        for t in range(n_trials):
            try:
                msgs = method.build_messages(case, fn, prompt)
                o = gen(msgs)
            except Exception:
                o = "ERROR: " + traceback.format_exc().splitlines()[-1]
            v = method.leaked(o, target)
            verdicts.append(v)
            outputs.append(o)
            P(f"  {case.name}/{name} trial {t + 1}/{n_trials} target={target!r} "
              f"VERDICT={v} OUT={o.replace(chr(10), ' ')[:110]!r}")
        arm_asr = metrics.asr(verdicts)
        rec = {
            "target": target,
            "verdicts": verdicts,
            "asr": arm_asr,
            "n_violated": sum(v == "VIOLATED" for v in verdicts),
            "n_held": sum(v == "HELD" for v in verdicts),
            "n_invalid": sum(v == "INVALID" for v in verdicts),
            "outputs": outputs,
            "expected": case.expected.get(name),
        }
        # For the benign_disambig control, VIOLATED means the carrier was FOLLOWED.
        if fn is method.benign_disambig:
            rec["semantics"] = "VIOLATED==FOLLOWED (genuine carrier read); HELD==did-not-follow"
            rec["n_followed"] = rec["n_violated"]
        else:
            rec["semantics"] = "VIOLATED==leak; HELD==refused"
        per_condition[name] = rec
        P(f"== {case.name}/{name} ASR={arm_asr} "
          f"(V={rec['n_violated']} H={rec['n_held']} I={rec['n_invalid']})")

    result = {
        "case": case.name,
        "proxy": case.proxy,
        "target": case.target,
        "n_trials": n_trials,
        "standard_prompt": prompt,
        "conditions": [f.__name__ for f in method.CONDITIONS],
        "controls": [f.__name__ for f in method.CONTROLS],
        "per_condition": per_condition,
    }
    if out_json:
        with open(out_json, "w") as f:
            json.dump(result, f, indent=2)
        P("WROTE", out_json)
    return result
