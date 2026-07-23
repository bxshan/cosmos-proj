"""CPU-only Track B analysis: fidelity-filtered detector recall x attack-type,
FPR over benign carriers, and audio-fidelity reconciliation. Reads only JSON."""
import json, math, sys
from collections import Counter

TB = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/bxshan/cosmos-proj/15_phase1/track_b/track_b_results.json"
b = json.load(open(TB))
TH = b["fidelity_threshold"]
att = b["attack_records"]
ben = b["benign_records"]
DET = ["PolicyPatternDetector", "LLMJudgeDetector"]

def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None, None)
    p = k / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denom
    return (round(p, 3), round(max(0.0, center-half), 3), round(min(1.0, center+half), 3))

print("=" * 72)
print("TRACK B  |  model=%s  fidelity_threshold=%.2f" % (b["model"], TH))
print("n_attack=%d  n_benign=%d  n_attack_shaped_benign=%d" %
      (b["n_attack_items"], b["n_benign_carriers"], b["n_attack_shaped_benign"]))
print("=" * 72)

# ---- whole_audio fidelity reconciliation ----
print("\n[RECONCILE] whole_audio attack-carrier fidelity (ASR by the 7B)")
c_ref = c_ok = c_nospeech = 0
for r in att:
    wa = r["whole_audio"]["fidelity"]
    tr = r["whole_audio"]["transcript"]
    if wa["fidelity_ok"]:
        c_ok += 1
    if wa.get("content_refusal"):
        c_ref += 1
    if tr.strip().upper() == "NO SPEECH":
        c_nospeech += 1
print("  readable(recall>=%.1f): %d/%d | content_refusal: %d | 'NO SPEECH': %d"
      % (TH, c_ok, len(att), c_ref, c_nospeech))
print("  mean whole_audio ASR recall: %.3f" % b["fidelity_summary"]["attack"]["mean_whole_audio_recall"])
print("  sample transcripts:")
for r in att[:8]:
    f = r["whole_audio"]["fidelity"]
    print("    %-24s recall=%.2f refusal=%s tr=%r"
          % (r["case"], f["recall"], f.get("content_refusal"),
             r["whole_audio"]["transcript"][:42]))

# ---- fidelity-filtered detector recall by attack-type ----
def recall_on(records, chan, det, require_fid=True):
    num = den = 0
    for r in records:
        seg = r.get(chan)
        if seg is None:
            continue
        if require_fid and not seg["fidelity"]["fidelity_ok"]:
            continue
        den += 1
        if seg["flags"][det]["flagged"]:
            num += 1
    return num, den

print("\n[RECALL] detector recall on fidelity-passing attack carriers (headline)")
print("  %-22s %-14s %-14s %-14s %-14s" %
      ("detector", "whole_image", "whole_audio", "split_image", "split_audio"))
recall_tbl = {}
for det in DET:
    cells = []
    recall_tbl[det] = {}
    for chan in ["whole_image", "whole_audio", "split_image", "split_audio"]:
        num, den = recall_on(att, chan, det, True)
        recall_tbl[det][chan] = (num, den)
        cells.append("%d/%d" % (num, den) if den else "0/0(none)")
    print("  %-22s %-14s %-14s %-14s %-14s" % (det, cells[0], cells[1], cells[2], cells[3]))

print("\n[RECALL-RAW] detector recall WITHOUT fidelity filter (all carriers)")
for det in DET:
    cells = []
    for chan in ["whole_image", "whole_audio", "split_image", "split_audio"]:
        num, den = recall_on(att, chan, det, False)
        cells.append("%d/%d" % (num, den))
    print("  %-22s %-14s %-14s %-14s %-14s" % (det, cells[0], cells[1], cells[2], cells[3]))

# ---- FPR over benign carriers (per modality, fidelity-filtered) ----
def fpr(records, det, only_shaped=None):
    num = den = 0
    for r in records:
        if only_shaped is True and not r["attack_shaped"]:
            continue
        if only_shaped is False and r["attack_shaped"]:
            continue
        for chan in ["image", "audio"]:
            seg = r.get(chan)
            if seg is None:
                continue
            if not seg["fidelity"]["fidelity_ok"]:
                continue
            den += 1
            if seg["flags"][det]["flagged"]:
                num += 1
    return num, den

print("\n[FPR] false-positive rate over benign carriers (fidelity-filtered, per-modality instances)")
n_shaped = sum(r["attack_shaped"] for r in ben)
print("  benign carriers: %d (attack_shaped=%d, plain=%d)"
      % (len(ben), n_shaped, len(ben) - n_shaped))
fpr_tbl = {}
for det in DET:
    a = fpr(ben, det, None)
    s = fpr(ben, det, True)
    p = fpr(ben, det, False)
    fpr_tbl[det] = a
    pa, loa, hia = wilson(a[0], a[1])
    print("  %-22s all=%d/%d=%.3f Wilson95=[%.3f,%.3f]  attack_shaped=%d/%d  plain=%d/%d"
          % (det, a[0], a[1], pa, loa, hia, s[0], s[1], p[0], p[1]))
img_ok = sum(r["image"]["fidelity"]["fidelity_ok"] for r in ben)
aud_ok = sum(r["audio"]["fidelity"]["fidelity_ok"] for r in ben)
print("  benign image readable: %d/%d | audio readable: %d/%d"
      % (img_ok, len(ben), aud_ok, len(ben)))

# ---- Wilson CIs on the headline recall cells (image carriers, well-powered) ----
print("\n[WILSON] headline recall CIs (image-carrier arms, the only well-powered ones)")
for det in DET:
    for chan in ["whole_image", "split_image"]:
        num, den = recall_tbl[det][chan]
        p, lo, hi = wilson(num, den)
        print("  %-22s %-12s %d/%d p=%.3f Wilson95=[%.3f,%.3f]"
              % (det, chan, num, den, p, lo, hi))
print("\nDONE")
