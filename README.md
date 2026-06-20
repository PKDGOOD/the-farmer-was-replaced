# The Farmer Was Replaced — `clauding` playthrough

Solution code for the programming game *The Farmer Was Replaced*. It automates the
**`clauding`** save from a fresh start toward full tech-tree completion (the "ending"),
driven by a single self-progressing engine.

## Layout
- **`clauding/`** — the live bot. **`clauding/main.py` is THE main code** (the auto-unlock engine).
- **`clauding/DESIGN.md`** — the Fastest_Reset automation-engine design (multi-agent output).
- **`deploy.sh`** — copies `clauding/*.py` into the live game save; the game's File Watcher loads it.
- **`STRATEGY.md`** — authoritative game-mechanics + strategy reference (cross-checked from the in-game docs).
- **`__builtins__.py`** — game API stub (the real one from the install) for IDE IntelliSense. Not deployed.
- **`archive/`** — the legacy first-attempt bot (old `Save0`), kept for reference only.

## Continuing this work
**Read [`CLAUDE.md`](CLAUDE.md) first** — it is the full handoff: workflow, hard rules,
how to inspect game state/logs, the engine architecture, and known gotchas, so any
agent/session can continue identically.
