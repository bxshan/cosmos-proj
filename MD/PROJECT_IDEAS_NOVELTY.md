# COSMOS Cluster 6 — Project Ideas, Ranked by Novelty

> Background / fallback bench (the novelty-first companion to `PROJECT_IDEAS.md`). **Superseded as the project choice** by the cross-modal injection thread. Five parallel scouts, ~100 searches. Scores: **5/5** = no student/hobbyist replication found or result <18 months old; **4/5** = research-active, thin tutorial trail; **3/5** = fresh angle on a saturated base. "Nothing surfaced in search" ≠ proof of absence; some figures are [vendor claim].

## Tier S (novelty 5/5) — the standouts
- **S1** iPhone-LiDAR see-around-corners (MIT *Nature* 653, May 2026; zero reimplementations; needs a Pro iPhone). Distinct from the older passive/penumbra corner camera.
- **S2** "Do modern deepfakes still lack a heartbeat?" — an April-2025 paper **overturns** FakeCatcher folklore (face-swaps inherit the driver's HR, rPPG corr **0.89**; a real detector only hits **87% AUROC**). Project = reproduce the debunking, then test rPPG on Sora/Veo-class full-generation video.
- **S3** spectral-fingerprint fragility (hand-crafted FFT/DCT deepfake detectors lose up to **83%** when peaks are surgically removed; deepest Kadambi-Fourier fit).
- **S4** "Images that Sound" (descoped to direct pixel-space optimization with CLIP + YAMNet losses — the purest 1-D↔2-D bridge).
- **S5** inverse cymatics (predict driving frequency from a Chladni-pattern photo; ~$40 kit, difficulty 2/5 — the low-risk frontier pick).
- **S6** sparse autoencoders on Whisper/wav2vec2 speech features (interpretability, validated against Praat F0/formants).
- **S7** watermark removal ≠ forensic evasion (removal cuts watermark-detection to 43% while an independent forensic classifier still catches >98%; most turnkey S-tier).
- **S8** colorism-in-beauty-filters pixel audit (luminance/ΔE2000 shift vs starting Monk/Fitzpatrick tone).
- **S9** low-light face detection stratified by skin tone (DarkFace + Poisson-shot-noise argument).
- **S10** Orbcomm satellite RF-fingerprinting ($25 RTL-SDR, ~$30–45 total).

**Tier A (4/5, 18 entries)** and **Tier B (3/5, 9 entries)** — narrowed twist-first versions across imaging / speech / bridge-sensing. Most turnkey audio idea: **A8** cross-generator voice-clone detection gap.

## AVOID list (the most consequential section — saturated framings; use only as a 2-min hook)
- **Media forensics:** train-a-CNN-on-real-vs-fake-faces; blink detection; corneal-reflection mismatch; plain C2PA/SynthID checking; plain audio real/fake classifier (no cross-generator test).
- **Fairness:** plain rPPG/pulse-ox skin-tone bias (**retreads Kadambi's own seed paper**; open fix `EquiPleth`; an existing undergrad capstone); Gender Shades replication; Shirley-card history; "AI draws CEOs white" prompt audit.
- **Bridge:** **the Visual Microphone itself** (open reproductions exist); Sound-of-Pixels/PixelPlayer; LipNet; plain image→sound sonification with no experiment; **bird-call spectrogram CNN** (a trap — looks like a bridge, is pure audio classification).
- **Physics-hacking:** WiFi-CSI presence/breathing/gesture; RTL-SDR ADS-B/NOAA-APT/hydrogen-line; webcam+grating spectrometer (74 repos); consumer Gaussian-splat scanning.

**Top picks:** max novelty → S1 or S2; deepest Fourier fit → S3; purest bridge → S4/S5; highest certainty → S7 or S8/S9; lowest hardware/skill risk → S5 or B2 (respiration-only).
