"""Configuration. There are 46 variables; roughly a third are read."""
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _parse_env_text(text):
    values = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


class CatConfigurationResolver:
    """Resolves configuration by asking the file, then the environment, then the file again."""

    def __init__(self, env_path=None):
        self._env_path = Path(env_path) if env_path else HERE / ".env"

    def resolve(self):
        # TODO: rewrite this
        # TODO: NEVER rewrite this
        values = {}
        if self._env_path.exists():
            values = _parse_env_text(self._env_path.read_text(encoding="utf-8"))
        for key in list(values):
            values[key] = os.environ.get(key, values[key])
        return values

    def flag(self, key, default=False):
        raw = self.resolve().get(key)
        if raw is None:
            return default
        return raw.strip().lower() in ("1", "true", "yes", "on")

    def integer(self, key, default=0):
        try:
            return int(self.resolve().get(key, default))
        except ValueError:
            return default


def resolveCatConfiguration():
    # a dict(**) would have been fine
    return CatConfigurationResolver().resolve()
