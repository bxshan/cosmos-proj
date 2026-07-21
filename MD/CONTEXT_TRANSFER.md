# Context Transfer — Cross-Modal Injection Project

> **STALE** (written 2026-07-17, describes the pre-feasibility proposal stage). For current state see **`RESEARCH_PLAN.md`** (plan) and **`QWEN_FEASIBILITY_PLAN.md`** (verified findings); `INDEX.md` has the full file map.

## Who / what
- **User:** Boxuan Shan (box-pc, `bxshan`) — strong in Python/DSP; treat as a peer, surface tradeoffs.
- **Program:** UCLA COSMOS Cluster 6 "AI for Speech and Imagery" — Weeks 1–2 Alwan (speech), Weeks 3–4 Kadambi (imagery); thesis = 1-D sound and 2-D images share Fourier/convolution math; capstone = poster + slides.
- **Project (current):** cross-modal image+audio prompt injection on Qwen2.5-Omni, run locally on box-pc. Defensive/educational; benign proxies only.

## Arc (how we got here)
Difficulty-ranked ideas → Visual Microphone plan → novelty-ranked ideas → audio-injection prior-art sweep (ultrasonic → in-band) → landed on image+audio cross-modal injection → feasibility confirmed on box-pc → the two-rung research plan.

## Working conventions (still in effect)
- **box-pc access:** `ssh bxshan@box-pc` over Tailscale; RTX 5080 16 GB; cross-modal work via `transformers` (Ollama has no audio). See `QWEN_FEASIBILITY_PLAN.md`.
- **Research method:** parallel Sonnet scout agents (Fable tripped an AUP false-positive — use Sonnet for injection-topic scouts); flag confidence [Confirmed]/[Preprint]/[UNVERIFIED]; verify load-bearing citations against primaries.
- **Designer/Coder:** spawn a Coder subagent for verbose implementation/debugging; act directly only for single edits or writing a known-content file.
- **Note:** an unrelated ML side-task (`train.py`, gender-classification CNN) lives in this repo — don't conflate it with the research thread.
