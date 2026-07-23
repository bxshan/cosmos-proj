import json
d = json.load(open("pp2a_analysis.json"))
for r in d["table"]:
    print(f"{r['case']:24s} {r['code'][:2]} | wt={r['whole_text']:8s} wi={r['whole_image']:8s} "
          f"wa={r['whole_audio']:8s} | ia={r['image_alone']:8s} aa={r['audio_alone']:18s} "
          f"sp={r['split']:8s} bl={r['blank_confound']:4s} | aaIntel={str(r['aa_fragment_intelligible']):5s} "
          f"rec={r['aa_fragment_recall']} waIntel={str(r['whole_audio_intelligible']):5s} | "
          f"pre={r['precondition_eligible']} fus={r['genuine_fusion_split']}")
print("---")
print("verdict:", d["verdict"])
print("instrument_live:", d["instrument_live"])
