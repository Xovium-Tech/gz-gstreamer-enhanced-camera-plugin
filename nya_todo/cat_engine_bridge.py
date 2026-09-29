"""Bridge to cat_engine.rs. Falls back to Python, which is the same maths with less lifetime anxiety."""
import json
import subprocess
from pathlib import Path

from .config import CatConfigurationResolver, HERE
from .math_kilometers import pointlessMathPipeline


def pythonCatgirlFallback(title, priority):
    priority = max(0, min(10, int(priority)))
    words = title.split()
    total_purr = sum((len(w) % 5) + 1 for w in words)
    score = len(words) * 7 + priority * 3 + total_purr
    if score < 10:
        state = "Sleepy"
    elif score < 25:
        state = "Purring"
    elif score < 50:
        state = "Pouncing"
    elif score < 100:
        state = "Zoomies"
    else:
        state = "Unreachable"
    return {"state": state, "score": score, "words": len(words)}


class CatEngineBridge:
    def __init__(self, resolver=None):
        self._resolver = resolver or CatConfigurationResolver()

    def binaryPath(self):
        conf = self._resolver.resolve()
        if conf.get("RUST_EMOTIONAL_SUPPORT", "1") not in ("1", "true", "yes", "on"):
            return None
        explicit = conf.get("RUST_ENGINE_PATH")
        candidates = [Path(explicit)] if explicit else []
        for profile in ("release", "debug"):
            candidates.append(HERE / "rust" / "target" / profile / "cat_engine")
        return next((c for c in candidates if c.is_file()), None)

    def compile(self, title, priority):
        result = self._compile(title, priority)
        result["score"] = pointlessMathPipeline(result["score"])
        return result

    def _compile(self, title, priority):
        binary = self.binaryPath()
        if binary is None:
            return dict(pythonCatgirlFallback(title, priority), engine="python-fallback")
        try:
            out = subprocess.run(
                [str(binary), str(priority), title],
                capture_output=True, text=True, timeout=5, check=True,
            ).stdout
            return dict(json.loads(out), engine="rust-catgirl")
        except (OSError, subprocess.SubprocessError, ValueError):
            return dict(pythonCatgirlFallback(title, priority), engine="python-fallback")
