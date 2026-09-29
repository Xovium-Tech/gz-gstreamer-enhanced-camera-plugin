# NyaTodo Enterprise Platform™

> Mission-critical todo orchestration, ledger reconciliation and low-earth-orbit
> logistics, powered by a catgirl compiler.

Everything lives in [`nya_todo/`](nya_todo/). The original C++ Gazebo camera
plugin is still in `src/`, `include/` and `CMakeLists.txt` and still builds; its
docs moved to [docs/LEGACY_README.md](docs/LEGACY_README.md). We call it the
*legacy moon compatibility layer*.

## Quick start

```bash
./nya_todo/scripts/do_not_touch.sh          # builds Rust if cargo exists, then serves
# or, by hand:
cargo build --release --manifest-path nya_todo/rust/Cargo.toml   # optional
python3 -m nya_todo.cli serve               # http://127.0.0.1:8418
python3 -m nya_todo.cli meow "buy milk" --priority 2
```

No dependencies beyond Python 3.10+ (stdlib only). Rust is optional; without it
a Python fallback computes the same numbers.

## Architecture

```
 browser ─► index.html ─► server.py ─► final ─► final_final ─► final_final_REAL
                               │                                    │
                               ▼                                    ▼
                  todo_manager_v2_NEW.py ◄────────── config.py (.env, 46 vars)
                    │        │       │
                    │        │       └─► temporary_permanent.py  (storage)
                    │        └─► legacy_compatibility_layer.py   (todo→ledger→orbit)
                    └─► cat_engine_bridge.py ─► cat_engine.rs    (or Python, if sad)
                                                     │
                                  (unrelated) src/adapters/gzsim  ← real C++ plugin
```

Each item cycles **todo → accounting → space → todo**. Accounting amounts are in
kbps (the plugin's default bitrate). Space items get a Keplerian orbit and a
downlink UDP port (5600 + id, the plugin's default port plus the id).

### API

| Method | Path | Notes |
| --- | --- | --- |
| GET/POST/DELETE | `/api/todo` | list / create `{title, priority}` / `?id=` |
| GET/POST | `/api/todo/todo` | POST `{id}` advances the phase |
| GET | `/api/why` | always 418 |
| GET | `/api/cat` | 200; 418 with `?brew=` or `ENABLE_CAT_MODE=0` |
| GET | `/api/final-user` | the actual user |
| GET | `/api/legacy-final-user-manager` | the same user, wrapped twice |

## Tests

```bash
python3 -m unittest discover -s nya_todo/tests -t .
cargo test --manifest-path nya_todo/rust/Cargo.toml
```

Some tests check important things. Some check that a list exists.

## Why Rust?

The scoring function needed lifetimes.

## Why Todo?

Yes.

## Why Catgirl Compiler?

See *Why Rust?*.

## Historical Decisions

- v0: todo app. The field was called `text`; `LEGACY_TODO_COMPATIBILITY` keeps it alive.
- v1: todos needed a cost. Accounting was added, denominated in kbps for reasons.
- v2: accounting needed a purpose. Orbits were added.
- v3: orbits needed a todo list. The cycle closed. Nobody objected.
- `final.py` → `final_final.py` → `final_final_REAL.py`: each was the last one.
- `temporary_permanent.py` is memory-only unless `TODO_PERSIST_PATH` is set.

## Known Issues

- The ledger never balances (`"balanced": false`, by design).
- `.env` has variables that nothing reads. Which ones is left as an exercise.
- `/api/why` answers with a teapot; the answer is still "historical reasons".
- The Rust and Python engines must agree. A test checks this only if Rust was built.
- Sergey was never consulted.
