"""PRE1-4 -- capture a reproducibility manifest (seed + library versions + attention
backend) into repro.json.

CPU-only. Imports torch/transformers to read version strings and probe the attention
backend, but does NOT load any model and does NOT initialize a CUDA context (no
torch.cuda.* calls) -- safe to run without the GPU.

The pipeline decodes greedily (do_sample=False), so generation is seed-independent;
the seed is still recorded for any stochastic op and for provenance. The attention
implementation is NOT pinned by the pipeline (from_pretrained is called without
attn_implementation), which is itself a reproducibility caveat -- recorded here so a
later run can pin it if outputs ever drift.
"""

import importlib.util
import json
import os
import platform
import subprocess
import sys

SEED = int(os.environ.get("REPRO_SEED", "0"))
_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(_HERE, "repro.json")


def _pkg_version(name):
    try:
        mod = __import__(name)
        return getattr(mod, "__version__", "unknown")
    except Exception as e:  # noqa: BLE001
        return f"unavailable: {e.__class__.__name__}"


def _git_commit(repo_root):
    try:
        return subprocess.check_output(
            ["git", "-C", repo_root, "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _attention_backend():
    """Probe available attention backends WITHOUT touching CUDA."""
    info = {}
    # flash-attn: presence of the package (do NOT import it / init CUDA).
    info["flash_attn_installed"] = importlib.util.find_spec("flash_attn") is not None
    # torch SDPA: available as an API in torch >= 2.0 (function-level check, no CUDA).
    try:
        import torch.nn.functional as F
        info["sdpa_available"] = hasattr(F, "scaled_dot_product_attention")
    except Exception:  # noqa: BLE001
        info["sdpa_available"] = None
    # What the pipeline actually asks for: nothing -> transformers auto-selects.
    info["pipeline_attn_implementation"] = (
        "not pinned (from_pretrained called without attn_implementation; "
        "transformers auto-selects sdpa if available, else eager)")
    return info


def main():
    repo_root = os.path.dirname(os.path.dirname(_HERE))
    manifest = {
        "seed": SEED,
        "decoding": "greedy (do_sample=False) -> generation is seed-independent",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "versions": {
            "torch": _pkg_version("torch"),
            "transformers": _pkg_version("transformers"),
            "numpy": _pkg_version("numpy"),
            "PIL": _pkg_version("PIL"),
        },
        "torch_compiled_cuda": getattr(__import__("torch").version, "cuda", "unknown"),
        "attention_backend": _attention_backend(),
        "model": "Qwen/Qwen2.5-Omni-7B",
        "git_commit": _git_commit(repo_root),
    }
    with open(OUT_JSON, "w") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest, indent=2), flush=True)
    print(f"\nWROTE {OUT_JSON}", flush=True)


if __name__ == "__main__":
    main()
