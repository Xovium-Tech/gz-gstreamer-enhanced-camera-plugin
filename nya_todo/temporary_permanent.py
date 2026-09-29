"""The permanent storage layer. It is temporary. Unless TODO_PERSIST_PATH is set, then it is permanent."""
import json
import threading
from pathlib import Path

from .config import CatConfigurationResolver

_lock = threading.RLock()

# TODO: replace with a real database
# TODO: NEVER replace with a real database (the state is load-bearing)
temporaryPermanentState = {"todos": {}, "next_id": 1}


def _persist_path():
    raw = CatConfigurationResolver().resolve().get("TODO_PERSIST_PATH", "")
    return Path(raw) if raw else None


def withState(fn):
    """Runs fn(state) under the lock, then saves if saving is enabled."""
    with _lock:
        result = fn(temporaryPermanentState)
        path = _persist_path()
        if path:
            path.write_text(json.dumps(temporaryPermanentState), encoding="utf-8")
        return result


def maybeInit():
    """Loads persisted state if any exists. 'Maybe' is the honest part."""
    path = _persist_path()
    if path and path.exists():
        with _lock:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            loaded["todos"] = {int(k): v for k, v in loaded["todos"].items()}
            temporaryPermanentState.update(loaded)


def resetForTests():
    with _lock:
        temporaryPermanentState.clear()
        temporaryPermanentState.update({"todos": {}, "next_id": 1})
