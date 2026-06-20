# CLAUDE.md — handoff context for the `clauding` playthrough

Read this fully before doing anything. It lets any new session/agent continue
identically. (Game = *The Farmer Was Replaced*, a programming game where you
script a drone in a Python-like — but NOT Python — language.)

---

## 1. Mission

Automate the **`clauding`** game save from scratch to the **endgame** (unlock the
whole tech tree) with one self-driving program, as tick-efficiently as possible.
`clauding/main.py` IS that program. We grew it stage by stage; it is now a
data-driven auto-unlock engine with parallel (multi-drone) farming.

**Current status (update this as you go):** Most of the tree is unlocked
(Megafarm, Mazes, Cactus, Polyculture, Sunflowers/Power, Simulation, Dinosaurs,
all crops + many upgrades). **Remaining feature unlock: `Leaderboard`.** The hard
bottleneck is **Gold** (from mazes). The engine pursues every affordable
upgrade/unlock and accumulates the valuable resources (gold/cactus/pumpkin/weird)
with **no resource caps**.

---

## 2. The golden workflow (how to make ANY change)

1. **Edit `clauding/main.py`** in this repo (never edit the live save directly).
2. **`./deploy.sh`** — copies `clauding/*.py` into the live save folder. It has a
   guard that REFUSES to deploy non-ASCII (see rule below).
3. **Tell the user to stop & re-run** the program in-game (File Watcher is ON, so
   the file updates automatically, but a running program must be stopped + replayed).
4. **Commit** to `main` (this repo commits straight to main; that's the convention).
   End commit messages with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
5. **Each work cycle, FIRST inspect game state** (see §4) — the user unlocks/plays
   between turns, so always re-read `save.json` before deciding what to change.

Live save folder:
`~/Library/Application Support/com.TheFarmerWasReplaced.TheFarmerWasReplaced/Saves/clauding/`

---

## 3. HARD RULES / gotchas (learned the hard way)

- **ASCII-ONLY in deployed `.py`.** The in-game code editor throws
  `IndexOutOfRangeException` (CodeWindow.OnCodeInserted) on non-ASCII (e.g. Korean)
  and garbles the running program. Keep Korean in chat/commits/`.md` only.
  `deploy.sh` blocks non-ASCII `.py`.
- **Gate every `plant()` that costs items with `afford_plant(entity)`** (uses
  `get_cost`). Calling `plant()` when you can't pay spams a game warning every tile
  and wastes cycles. (Cactus costs items; carrots cost wood+hay; pumpkin costs
  carrots; etc.)
- **Bound EVERY `while` loop.** An unbounded `while not can_harvest()` (e.g. waiting
  on a tile that has no plant) hangs the whole program — the #1 cause of "it keeps
  stopping". Every wait loop has a `tries < N` cap and an early-exit.
- **Drones (Megafarm):** `spawn_drone(fn, *args)` runs `fn(*args)` on a new drone at
  the spawner's position; returns a handle or `None` at the cap. **No shared memory**
  (each drone copies globals); coordinate via the shared farm state + inventory only.
  Return values come back via `wait_for(handle)`. Split work by row/column so drones
  never touch the same tile (no races). `parallel_rows`/`parallel_cols`/`parallel_rows_arg`
  are the helpers. A hung drone deadlocks `wait_for`, so worker loops MUST be bounded.
- **`use_item(item, n)` is one 200-tick action regardless of `n`** — batch it.
- **No resource caps.** The user explicitly does NOT want reserve caps — the engine
  must keep accumulating valuable resources for upgrades, not idle on basic crops.
- **Tick model:** productive actions (move/harvest/plant/swap/till/use_item/unlock/
  spawn_drone) = 200 ticks on success, 1 on fail; sensors (measure/can_*/get_*/
  num_items/get_companion) = 1 tick; `print` ≈ 400 ticks (NEVER use); `quick_print`/
  `get_tick_count`/`get_time` = 0 ticks. The whole game = minimize successful 200-tick
  actions and moves. Power (from sunflowers) makes the drone act 2x faster.

---

## 4. Inspecting game state & logs

- **Unlocks + item stocks:** read `Saves/clauding/save.json` (JSON). Keys: `unlocks`
  (lowercase internal ids, upgrades suffixed `_N`, e.g. `megafarm_2`), `items`.
  Always check this at the start of a cycle.
- **Program output / `quick_print`:** `~/Library/Application Support/com.TheFarmerWasReplaced.TheFarmerWasReplaced/output.txt`
  (written on stop). `main.py` logs `tick / gold / cact / pump / weird / power` each loop here.
- **Runtime errors / crashes:** `~/Library/Logs/TheFarmerWasReplaced/TheFarmerWasReplaced/Player.log`.
  (Ignore the recurring `IndexOutOfRangeException @ CodeWindow.OnCodeInserted` / `ThreadAbort` —
  those are the editor/stop, not the script. A program HANG shows as the output.txt log
  simply stopping.)

---

## 5. Authoritative game docs (ground truth — NOT the repo copies)

The installed game has the real docs + the newest API stub:
`~/Library/Application Support/Steam/steamapps/common/The Farmer Was Replaced/TheFarmerWasReplaced_Data/StreamingAssets/Languages/`
- `builtins.py` (2321 lines) — every builtin + exact tick costs + full enums.
- `EN/docs/unlocks/*.md` — authoritative mechanics + the spoiler/algorithm HINTS.
- `EN/docs/scripting/*.md` — the (non-Python) language semantics.

`STRATEGY.md` (repo root) distills all of this. Where it ever disagrees with the
in-game `unlocks/*.md`, trust the in-game docs (e.g. cactus row-then-column sort IS
correct; sunflower bonus is 8x; pumpkin yield is `s^3` for s<=5 then `6*s^2`).

---

## 6. `clauding/main.py` architecture

- **`run()`** loop each cycle: (0) keep Power topped (`power_gen`) → global 2x;
  (1) buy every affordable upgrade/unlock from `all_targets()`; (2) farm toward the
  nearest **fundable** un-affordable target's bottleneck item (`worst_item`), with
  NO caps. `fundable()`/`can_produce()` skip targets whose missing items we can't
  make (e.g. needs Bone) so it never stalls.
- **`produce(item)`** dispatches to a routine: `Gold` → `maze_run` (or build weird via
  `pumpkin_batch` first); `Weird_Substance`/`Pumpkin` → `pumpkin_batch`; `Cactus` →
  `cactus_once`; `Hay`/`Wood`/`Carrot` → `balanced_sweep`.
- **Farming routines** (all multi-drone via `parallel_rows`/`_cols`):
  `balanced_sweep` ( `(x+y)%3` → tree / carrot / grass ), `pumpkin_mega_once`
  (fertilize-in-place → mega + weird_substance), `cactus_once` (row-sort then
  col-sort → `(size^2)^2` cascade), `power_gen` (sunflowers → parallel max-petal
  reduction → harvest only the field-max for 8x power), `maze_run` (make a maze from
  weird_substance, race wall-following `searcher` drones to the treasure → gold).

### The progression pipeline
`fertilized pumpkin → weird_substance → maze → gold → upgrades/unlocks`, plus
sunflowers → power → global 2x. Mazes consume `size * 2^(mazeLevel-1)` weird each
and yield gold = maze area.

---

## 7. Next optimizations (from the multi-agent CS analysis, ROI-ranked)

Applied: Power 2x (done), bounded loops, afford-gated planting, no-cap engine.
**Still TODO (highest value first):**
1. **Maze `measure()`-guided solving** — `measure()` returns the treasure (x,y) from
   anywhere; replace blind wall-following with directed search → ~17-25x fewer moves
   on the GOLD bottleneck. (Risky; bound it.)
2. **Polyculture** — `get_companion()` is unused; satisfying it multiplies yield ×5→×20.
3. **Cactus cocktail/odd-even sort** — drop the per-pass rewind → ~4x fewer ops.
4. **`simulate()`** (Simulation is unlocked) — deterministic offline A/B tuning of params.
5. **`use_item(item, n)` batching** everywhere.

When in doubt about mechanics or the optimal algorithm, re-read the in-game
`unlocks/*.md` hints (§5) — they spell out the intended algorithms.
