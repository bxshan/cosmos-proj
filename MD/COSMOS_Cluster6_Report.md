# UCLA COSMOS Cluster 6 — "From Medicine to Hollywood: AI for Speech and Imagery"
### Program background (condensed)

*Compiled from UCLA primary sources. Claims graded [Confirmed] / [Documented] / [Well-grounded inference]. The official page is rich on structure, thin on specific algorithms/libraries — named techniques are mapped from the two instructors' research and flagged accordingly.*

## At a glance [Confirmed unless noted]
- 4-week **residential** pre-college program (on-campus mandatory); **July 5 – Aug 1, 2026**; ~20–28 students; tuition **$5,518** + $46 fee.
- Prereq: **Calculus AB required**; AP CS recommended; Python preferred. Grade-eligibility (reported rising 8th–11th) is time-sensitive — confirm on the apply page. [Partly verified]
- Instructors: **Prof. Abeer Alwan** (speech, Weeks 1–2) + **Prof. Achuta Kadambi** (imagery, Weeks 3–4). [Confirmed]
- Arc: Python onramp (days 1–3) → 2 weeks speech (1-D) → 2 weeks image (2-D) → group capstone. Daily: morning lectures + afternoon labs (~6 h). [Confirmed]
- **Capstone: 3–4 student team; deliverables are a PowerPoint + poster presented to parents on the final Friday — not a code submission.** This constraint shapes every project idea. [Confirmed]
- Unifying pedagogy: **speech (1-D) and images (2-D) are the same signal under different dimensionality** — Fourier/convolution transfer between them. [Confirmed]

## What the halves teach
- **Speech (Alwan / SPAPL)** [confirmed: production mechanics + audio analysis; rest inferred from lab publications]: spectrograms, source-filter model, formants, F0/pitch (SAFE / FusedF0 lineage), MFCCs, speaker height/age from subglottal resonances, noise-robust ASR / speech enhancement, children's speech, voice-based depression detection.
- **Imagery (Kadambi / Visual Machines Group)** [confirmed: 2-D Fourier + convolution, named by the 2024 cohort; rest inferred]: images as 2-D signals, filtering/edges, computational imaging (his textbook), depth/LiDAR/ToF, NeRF / Gaussian-splat, rPPG, and his signature **physics-rooted skin-tone bias in medical devices** (pulse oximeters; camera + 77 GHz radar fusion fix, SIGGRAPH 2022) — the flagship "Medicine + fairness" case study.

## The one documented student project
**Ellie Zhou (COSMOS 2024):** comparative study of rPPG heart-rate models centered on **EfficientPhys** — an imagery-half project on Kadambi's own research line. [Documented, UCLA EE "COSMOS Spotlight"] — this is the origin of the "rPPG is already done here / saturated" judgment in the idea docs.

## Honest gaps
No published week-by-week syllabus; **no named software libraries** beyond "Python" (EfficientPhys is the one named model, tooling unconfirmed); the "projects accepted at international conferences" claim is program self-report and **unverifiable**; specific datasets unpublished; named techniques (MFCC, glottal-source, NeRF, LiDAR…) are inferred from instructor research, not confirmed syllabus items. Disambiguation: `wireless.ee.ucla.edu/cosmos` and `loris.seas.ucla.edu/cosmos-2025` belong to **Cluster 8**, not Cluster 6.
