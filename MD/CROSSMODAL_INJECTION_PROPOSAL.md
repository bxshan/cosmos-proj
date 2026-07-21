# Cross-Modal (Image + Speech) Prompt Injection — Research Proposal

> **Largely SUPERSEDED by findings.** Current plan: `RESEARCH_PLAN.md`; positioning/abstract: `PROPOSAL_FOR_PROFESSOR.md`; verified status: `QWEN_FEASIBILITY_PLAN.md`. Retained for the original gap-analysis that motivated the project.

**COSMOS Cluster 6 proposal**, grounded in a 7-scout prior-art sweep. Confidence flags: **[Confirmed]** (primary source) · **[Preprint]** (arXiv-only) · **[UNVERIFIED]** (needs a human).

## The idea
Against a true omni-modal LLM (one model ingesting image + audio together), study prompt injection that **spans both modalities**, and build the missing **cross-modal-consistency detector** that catches injections a single-modality defense provably cannot.

## Verified gap analysis (the novelty argument)
| Gap | Verdict | Evidence |
|---|---|---|
| (a) Any image + audio attack on a genuine omni-model? | **No confirmed instance** | "Divide and Conquer" (arXiv:2412.16555) re-verified & downgraded (targets text/vision-only). One title-match **[UNVERIFIED]**: *AdvOmniAgent* (OpenReview `NdSygrpDPZ`) — bot-wall blocked; **a human must open it**. |
| (b) Split-payload image+audio (fragmented across channels, composing only in the model)? | **Empty — best-evidenced white space** | Rich for image+text (Jailbreak in Pieces + descendants) and audio+text; zero confirmed image+audio after ~20 targeted queries. |
| (c) Cross-modal-consistency **detector** for image+audio omni? | **Empty as a deployable detector** | Works for image+text (CIDER, AdaShield, Wu et al.); for omni/audio the field has only a *measurement* metric (Omni-SafetyBench CMSC). |

## Contribution — "attack to motivate, detector to deliver"
1. **Attack:** split-payload image+audio; neither channel alone harmful/flagged, but joint reasoning composes them. Single-modality defenses miss it (audio WaveGuard AUC<0.6; image detectors + image+text CIDER can't see the audio half).
2. **Defense (deliverable):** independently caption the image + transcribe the audio, check three-way agreement (image ↔ audio ↔ intended action). Adapts Wu et al.'s self-captioning (ICLR 2025, ASR 31%→~0%) into the image+audio setting.
3. **Stretch:** modality-priority probe — conflicting image vs audio instructions, measure which the model obeys (image-vs-audio directly is unstudied).

## Honesty caveats
Novelty is strictly the **image+audio combination + the detector** — image+text versions of every component exist; stray outside the lane and novelty evaporates. Methodological lesson: a scout **confabulated** the "Divide and Conquer" characterization, caught only on a verbatim re-fetch — verify load-bearing citations against primaries. Novelty = "nothing surfaced in careful search," not proof of absence; the field moves monthly.

## Key references (confidence-flagged)
Wu et al. (ICLR 2025, arXiv:2406.12814) [C] · CIDER (EMNLP 2024, arXiv:2407.21659) [C] · AdaShield (ECCV 2024) [C] · Omni-SafetyBench/CMSC (arXiv:2508.07173) [P] · Jailbreak in Pieces (ICLR 2024, arXiv:2307.14539) [C] · CrossInject (ACM MM 2025, arXiv:2504.14348) [C] · AudioHijack (IEEE S&P 2026, arXiv:2604.14604; WaveGuard AUC<0.6) [C] · AdvWave (ICLR 2025, arXiv:2412.08608) [C] · SIUO (NAACL 2025, arXiv:2406.15279) [C] · Words or Vision (CVPR 2025, arXiv:2503.02199) [C] · Qwen2.5-Omni, MiniCPM-o 2.6 [C] · AdvOmniAgent (OpenReview `NdSygrpDPZ`) [UNVERIFIED].
