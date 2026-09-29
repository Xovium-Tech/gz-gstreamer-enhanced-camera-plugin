#!/usr/bin/env bash
# Builds the catgirl compiler (if cargo exists), then serves. Usage: ./nya_todo/scripts/do_not_touch.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
if command -v cargo >/dev/null 2>&1; then
  cargo build --release --manifest-path nya_todo/rust/Cargo.toml
else
  echo "cargo not found; the Python fallback will do the meowing" >&2
fi
exec python3 -m nya_todo.cli serve
