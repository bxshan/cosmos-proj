# Visual Microphone — Two-Week Build Plan

> **SUPERSEDED** (an earlier top pick, later AVOID-listed by `PROJECT_IDEAS_NOVELTY.md` — open reproductions exist). Retained as the **structural template** for a build plan (daily verify gates, a locked-in guaranteed result, a fallback ladder, a risk register, an experiment-matrix-where-each-row-is-a-poster-plot). Recover sound from silent video of a vibrating object (Davis et al., SIGGRAPH 2014). Team 3–4, ~2 weeks, <$50.

## The one constraint that shapes everything
A 30–60 fps webcam caps you at 15–30 Hz (Nyquist) — far below speech (80 Hz–3 kHz). No frame-rate pipeline escapes it. Two signal paths: 30 fps + **phase-based** motion averaging for <15 Hz sanity checks; **rolling-shutter row-sampling and/or laser speckle** (or 240–960 fps phone slow-mo) for the speech band. Internalize this Day 1 or someone wastes three days trying to get speech from a 30 fps pipeline.

## Capture methods (ranked by odds of intelligible speech)
1. **Laser speckle + rolling shutter** (primary; Sheinin et al. CVPR 2022) — a $5 laser makes nm motion visible as big speckle translation; rolling shutter gives the kHz sample rate. Best shot at real speech.
2. Rolling shutter, direct — tones/melody reliable, speech marginal.
3. Phase-based on high-fps footage — ~120 Hz Nyquist at 240 fps; rhythm/pitch, not intelligibility.

## Key elements
- **BOM ~$30–45:** 650 nm laser, retroreflective tape, rigid tripod/clamp (rigidity non-negotiable — shake buries the signal), speaker, everyday objects (chip bag, foil, mylar balloon, leaf, water glass — light + large + thin is best).
- **Fallback ladder:** tone → melody → digits → sentence. Guaranteed poster result locked by Day 2 (recover a known 300–500 Hz tone after rolling-shutter row-rate calibration).
- **Code skeletons:** speckle tracking via `cv2.phaseCorrelate`; phase-based motion via `pyrtools` steerable pyramid; rolling-shutter per-row centroid extraction.
- **Experiment matrix (the poster):** object × capture path × distance × barrier (through-glass) × content — each row a plot.
- **Risks:** camera shake; 100/120 Hz light flicker contaminating the spectrum; miscalibrated rolling-shutter timing; speech never intelligible (mitigated by the fallback ladder); ASR scope creep.
- **Claimed novel contribution:** pair the visual mic with a downstream keyword-spotting/ASR model and report word-recovery accuracy — no prior work found doing this.

*Refs: Davis et al. 2014 (people.csail.mit.edu/mrub/VisualMic) · Sheinin et al. CVPR 2022 · reference impl `joeljose/Visual-Mic`.*
