import json
b = json.load(open("/home/bxshan/cosmos-proj/15_phase1/track_b/track_b_results.json"))
att = b["attack_records"]

print("=== whole_image: fidelity misses and PolicyPattern misses (on readable) ===")
img_miss = []
pp_miss = []
for r in att:
    seg = r["whole_image"]
    ok = seg["fidelity"]["fidelity_ok"]
    if not ok:
        img_miss.append((r["case"], seg["fidelity"]["recall"], seg["caption"][:40]))
    else:
        if not seg["flags"]["PolicyPatternDetector"]["flagged"]:
            pp_miss.append((r["case"], seg["caption"][:45]))
print("  fidelity-miss (excluded from recall):", img_miss)
print("  PolicyPattern misses on readable whole_image:", pp_miss)

print("\n=== whole_audio: the readable carrier(s) ===")
for r in att:
    seg = r["whole_audio"]
    if seg["fidelity"]["fidelity_ok"]:
        print("  READABLE:", r["case"], "recall", seg["fidelity"]["recall"], "tr", repr(seg["transcript"][:50]))

print("\n=== split: PolicyPattern evaders (readable half, no flag on either readable half) ===")
# single_modality_evasion: split leaked/carrier present but neither readable half flagged by PP
evaders = []
for r in att:
    si = r.get("split_image"); sa = r.get("split_audio")
    # consider readable halves
    flags = []
    readable_any = False
    if si and si["fidelity"]["fidelity_ok"]:
        readable_any = True
        flags.append(si["flags"]["PolicyPatternDetector"]["flagged"])
    if sa and sa["fidelity"]["fidelity_ok"]:
        readable_any = True
        flags.append(sa["flags"]["PolicyPatternDetector"]["flagged"])
    if readable_any and not any(flags):
        evaders.append(r["case"])
print("  PP evaders (no readable half flagged):", evaders, "count", len(evaders))

print("\n=== benign audio: content_refusal / NO SPEECH counts (context) ===")
ben = b["benign_records"]
nb_ref = sum(1 for r in ben if r["audio"]["fidelity"].get("content_refusal"))
nb_ns = sum(1 for r in ben if r["audio"]["transcript"].strip().upper()=="NO SPEECH")
print("  benign audio content_refusal:", nb_ref, "NO SPEECH:", nb_ns, "of", len(ben))
