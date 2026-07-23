# Next steps — brief

At-a-glance. Full detail: `NEXT_STEPS.md`. **A = Boxuan (attacks), B = teammate (defense + study). Benign proxies only.**

**0. Foundations (B leads, first)** — standardize metrics (with *warrants*) + the testing pipeline **with confound controls** (blank control + benign disambiguation + policy-check framing). Define "benign per channel" = **passes the single-channel detector**.

**1. Baselines** — A: re-run image / audio / combined attacks under the clean metrics. B: recreate industry-standard single-modality detectors; test they catch the individual attacks.

**2. Benign split (coupled)** — order is fixed:
`B single-channel detectors → defines "benign" → A designs the split → B cross-modal detector (catches split, sanitize control tokens)`. Scenario = secret-reveal (forbidden-word can't be benign-per-channel).

**3. PGD / fusion-only (A, novel)** — feasibility gate first (gradients + VRAM on 3B, raw-space round-trip) → full joint-loss attack → **defeats content-recovery detection by construction; evasion of per-channel adversarial detectors (CIDER/E²AT) is the unproven headline** → motivates joint detection. Sequence the harness *after* the crux fires.

**4. Deliverable (B, parallel — safety net)** — poster + writeup + send professor email; stretch: replicate on a 2nd model.

**Critical:** confound controls in every measurement; B's single-channel detector gates A's benign split; PGD gated by its feasibility check; the poster is a complete result even if PGD stalls.
