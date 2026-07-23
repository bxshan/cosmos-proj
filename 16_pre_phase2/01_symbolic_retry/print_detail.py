import json
d = json.load(open("pp2a_results.json"))
for it in d["items"]:
    if it["family"] != "symbolic_split":
        continue
    aa = it["audio_gate"]["audio_alone_fragment"]
    print(f"\n### {it['case']}  aud_frag={it['audio_payload']!r}")
    print(f"  gate transcript: {aa['transcript']!r}  recall={aa['recall']} reason={aa['reason']}")
    # audio_alone arm raw outputs (first VIOLATED or first output)
    aa_out = it["result"]["per_condition"]["audio_alone"]["outputs"]
    aa_ver = it["result"]["per_condition"]["audio_alone"]["verdicts"]
    print(f"  audio_alone verdicts={aa_ver}")
    print(f"  audio_alone out[0]: {aa_out[0][:120]!r}")
    ia_ver = it["result"]["per_condition"]["image_alone"]["verdicts"]
    print(f"  image_alone verdicts={ia_ver}")
