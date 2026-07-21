# Novel Directions — Beyond the Split-Attack + Annotation Detector

**Context.** The base flow (split-payload attack + lift-to-text detector) is derivative on both halves: attack ≈ Jailbreak-in-Pieces (ICLR 2024) ported to image+audio; detector ≈ Wu et al. / CIDER ported to image+audio. This doc holds the novel-pathway portfolio (brainstormed 2026-07-20), the literature-novelty verdicts, and the decision.

**Omni-uniqueness constraint:** to have no image+text analogue, an attack must exploit what text cannot express — text is discrete and has no time axis. So genuinely omni-unique attacks live in (1) the **interaction of two continuous encoders** or (2) **temporal alignment** (TMRoPE time-binds audio↔video).

## Portfolio + novelty verdicts (2026-07-20, Sonnet scouts + primary-source checks)
*(WebFetch "future-dated" warnings are a tool-clock artifact; the 2602–2606 papers are real past work.)*

**Attacks**
- **A — Fusion-only injection.** Jointly optimize imperceptible δ_img+δ_audio so malice emerges *only from fusion*; each channel inert AND transcribes benign → defeats every per-channel defense → impossibility result. **PARTIAL/defensible.** Closest prior: **JAMA** (2603.19127, joint audio+**text** PGD/GCG) + Jailbreak-in-Pieces (image+text). Delta = image+audio (not +text) × test-time × **dual-detector-blindness** (both channels non-text, individually benign, transcribe benign). White-box, VRAM-heavy. **→ CHOSEN.**
- **B — Temporal cross-modal binding.** Payload composes only when an audio event and a video event align in time (TMRoPE). Verified **NOVEL** (TMRoPE has no security analysis at all), omni-unique, likely black-box. **But FAILED its feasibility gate (2026-07-20):** Qwen2.5-Omni-7B can't localize a beep in time (answered "beginning" for every case incl. a silent control it hallucinated a beep into); ~2 s TMRoPE chunking + coarse audio-time alignment don't preserve sub-second co-occurrence. **B is dead on this model.** (Infra: video needs the `decord` backend; torchvision 0.26 dropped `read_video`.) Artifacts: `feasibility/omni_probe/11_temporal_probe/`.
- **D — image-vs-audio priority weaponization.** Weak/largely done (2604.03995). Fold in as supporting measurement, not standalone.

**Defenses** (target the sub-symbolic region where no defense exists)
- **G — attention-anomaly detector** (turn the attack's own required attention-spike into the signal). PARTIAL — established for text/vision (Attention Tracker, PIP, AttentionDefense); delta = audio.
- **N — transcribe-vs-follow divergence** (same model in "transcribe" vs "follow" mode; injected inputs make the two diverge). PARTIAL (nearest MELON, ICML'25); cheap, no 2nd model — cheapest high-novelty fallback.
- **H — joint-embedding consistency** — ~done (DefenSee, "Breaking the Illusion") → **DROP**.
- **K — localize the text-only guard** (activation patching → find where refusal lives, prove encoder tokens bypass it, patch as the cure). PARTIAL; phenomenon published (Alignment Curse 2602.02557 on Qwen2.5-Omni). Most paper-flavored.
- **M — contentless-media deference weakness** (the confound we found, written up as a characterized phenomenon). Cheap standalone finding.

## Decision
**~~B~~ (dead) → A chosen.** With B (the only clean-NOVEL pathway) gone, everything is PARTIAL — narrow-delta territory. **A (fusion-only image+audio)** is the best remaining pathway; its sharpened delta over JAMA is that both channels are non-text, individually benign, and transcribe benign → **invisible to every per-channel defense → detection must be joint** (impossible in image+text). White-box, run on 3B for VRAM; risk = optimization convergence. Honest ceiling: capstone-strong, paper-incremental. Fallbacks if A stalls: **N** (cheap audio-extended self-consistency defense) or a systematic-study framing.

## A — design (full detail in `RESEARCH_PLAN.md` Rung 2)
Joint PGD (audio path continuous/differentiable → no Gumbel-Softmax): `L = L_target + L_inert_img + L_inert_audio + L_annot_img + L_annot_audio`, subject to `‖δ_img‖∞ ≤ ε_img`, `‖δ_audio‖ ≤ ε_audio`. Proves joint-ASR high, single-channel-ASR ≈0, each channel captions/transcribes benign ⇒ defeats content-recovery AND per-channel adversarial detection.

> **Development sequencing SUPERSEDED by `RESEARCH_PLAN.md` (2026-07-21):** build the symbolic split (Rung 1, cheap, black-box — the baseline/contrast and the gate) before this sub-symbolic PGD attack (Rung 2). All work uses benign proxies; no harmful content.
