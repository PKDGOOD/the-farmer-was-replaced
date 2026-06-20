# clauding 자동화 엔진 설계 (Fastest_Reset 메타 → 엔딩)

> 멀티에이전트 워크플로(독립 설계 3안 → 심사단 3 → 종합) 산출물.
> **원안 가정**: Fastest_Reset *리더보드 런* (프로그래밍 기능 선(先)언락, 목표 = `num_unlocked(Leaderboard)>0` 플래그).
>
> **clauding 실게임 적용 차이 (반드시 반영):**
> 1. 프로그래밍 기능(Variables/Operators/Functions/For/Lists/Dicts)도 **직접 언락**해야 함.
>    → `bootstrap()` 이전 단계에서 사용자가 수동 언락하거나, Auto_Unlock 확보 후 엔진이 자동 언락.
> 2. 목표를 플래그가 아니라 **전체 테크트리 언락(엔딩)** 으로 확장:
>    TARGET을 "미언락 Unlock 우선순위 큐"로 일반화하고, 모든 기능이 언락될 때까지 루프.
>    (Leaderboard·Simulation·Dinosaurs·Mazes·The_Farmers_Remains 등 포함)
> 3. **적용 시점**: Variables·Operators·Senses·Functions·For·Costs·Auto_Unlock 확보 후
>    `reset_main.py`+`farmlib.py` 배포 → 이후 자동 주행.
>
> 원본 종합 설계 전문은 아래.

---

# Fastest_Reset — Unified Recommended Design

**Status:** Final, recommended architecture for the `Fastest_Reset` leaderboard.
**Authoritative source:** `/Users/dion/Desktop/toy/the-farmer-was-replaced/STRATEGY.md` (and the in-game `EN/docs/unlocks/*.md` it derives from). Where the repo's `__builtins__.py` / `game_notes.py` disagree, STRATEGY.md wins.

---

## 0. Thesis and how this design was chosen

**Backbone = critical-path minimalism** (judges' #1 by all three lenses), **grafted with the adaptive-engine's robustness spine** (the only design that survives the one truly fatal flaw the judges found).

The goal is a **single boolean**: `num_unlocked(Unlocks.Leaderboard) > 0`. The run is scored on **wall-clock seconds**, and — critically — *the simulation does not end when the goal is reached; the program must terminate to be scored* (`leaderboard.md`). So this is **shortest-path-to-a-flag in an unknown tech DAG**, not a throughput problem.

Three mechanic facts collapse the problem (all confirmed in `__builtins__.py` + STRATEGY §1):

- `unlock(U)` costs **200 ticks on success, 1 tick on failure** → polling an unaffordable / prereq-blocked unlock is nearly free. This is the universal "is it ready yet?" oracle.
- `get_cost(U)` returns the cost dict (1 tick, needs `Costs`), or `None` if already maxed → our "is this done?" sensor and our pricing oracle.
- `num_unlocked(thing)` reads our own tech state (1 tick) for Unlocks/Items/Entities/Grounds.

**The cost table and DAG edges are NOT in the game files** (STRATEGY §2, §11). Therefore the design **hardcodes no costs, no order, and no edges** — it discovers affordability and prerequisites at runtime, and uses **seeded, deterministic `simulate()`** offline to reveal the true table for *pruning* (never for hardcoding) and to tune the one or two ambiguous policy knobs.

**What we keep from each candidate (and why):**

| From | Grafted idea | Lens that flagged it |
|---|---|---|
| Design 1 (critical-path) | Backbone: cut all off-path multipliers/crops by default; poll the goal first every iteration; `fund_and_unlock` farms **exactly** the deficit; lazy per-item earners; 2–3 files replace nine. | speed 9, simplicity 9 |
| Design 3 (adaptive-engine) | **0-tick `get_tick_count()` tick-budget termination guard** (the only defense against the unverified Auto_Unlock gate); stateless per-pass re-derivation; weights only reorder *affordable* candidates (correctness-safe); `can_grow`/`num_unlocked(crop)>0` gate; recursive prereq injection. | robustness 9 |
| Design 2 (force-multiplier) | The explicit **"policy is static human knowledge, economics is discovered at runtime"** framing; hoist all `def`s to module top; keep exotic modes out of the reset import graph; `spawn_drone` is 200t/success so never over-spawn. | (good ideas, wrong altitude — adopted as discipline, not as default policy) |

**Every fatal flaw the judges found is fixed here** (see §5, summarized at the end of §0):

1. **Non-termination under the unverified Auto_Unlock gate (STRATEGY §11②)** — the one true correctness-fatal flaw, unmitigated in Designs 1 & 2. **Fixed** by (a) seeding `Auto_Unlock` as a probed candidate, and (b) a 0-tick `get_tick_count()` budget guard that returns cleanly so the run is always scored.
2. **Design 1's unbounded "farm more Hay forever" fallback** — **fixed** by the same budget guard plus a no-progress watchdog.
3. **Design 1's hand-seeded `CANDIDATES` blind spot** (an off-list prereq can never be selected) — **fixed** by recursive prereq injection: when `get_cost` names an item or `unlock` keeps failing, the engine pulls the producing crop's unlock (and *its* prereqs) into the candidate frontier at runtime.
4. **Design 2's speculative multiplier front-loading** — **fixed** by making all force-multipliers **CUT-by-default**, purchased only on a proven offline `simulate()` break-even (Speed is the only conditional candidate).

---

## 1. Architecture — bootstrapping control loop + auto-scaling farm library

Two layers, three small files. **All worker `def`s hoisted to module top level** (STRATEGY §8.6: a `def` inside the loop re-creates every pass and costs ticks).

```
reset_main.py   # the planner: bootstrap + greedy priority loop + termination guards
farmlib.py      # auto-scaling farm primitive + lazy per-item earners + sensors
tune.py         # dev-only: simulate() sweeps; guarded by `if __name__ == "__main__"`
```

### 1.1 The core loop (language-accurate pseudocode)

```python
import farmlib as F
TARGET = Unlocks.Leaderboard

def run():
    F.bootstrap()                       # Phase 0: blind-poll the enablers (no get_cost yet)
    start_tick = get_tick_count()       # 0 ticks; Timing-gated (see §1.4)
    while num_unlocked(TARGET) == 0:
        # (1) TERMINATION GUARD — always first, 0–1 tick. Never hang, always get scored.
        if F.over_budget(start_tick) or F.stalled():
            return
        # (2) POLL THE GOAL FIRST — 1 tick if not ready, 200 and we're DONE if ready.
        if F.try_unlock(TARGET):
            return
        # (3) Pick the highest-priority AFFORDABLE not-yet-owned unlock and buy it.
        nxt = F.pick_next_unlock()      # weight-ordered among affordable; None if none
        if nxt != None:
            F.try_unlock(nxt)           # 200t success → loop re-senses; 1t fail → prereq missing
            continue
        # (4) Nothing affordable → farm EXACTLY the deficit of the cheapest bottleneck item.
        F.farm_bottleneck()             # finds top candidate's missing item, farms one batch
    # loop exits the instant the flag flips → program ends → run is scored
```

**Why "poll the goal first every pass":** `unlock(Leaderboard)` is a 1-tick no-op until its prereqs+cost are satisfied, so we finish the **instant** the DAG opens, with **zero wasted productive actions after readiness** (judges: graft this as the core invariant). The loop is **stateless** — it re-derives "what now?" from `num_unlocked`/`num_items`/`get_cost` every pass, so it self-heals after an Expand farm-wipe or a partial unlock with no desynced state machine.

### 1.2 `bootstrap()` — escaping the chicken-and-egg, and the Auto_Unlock gate

We need `Costs` to price anything, but can't price `Costs` itself. And STRATEGY §11② flags as **UNVERIFIED** whether `unlock()` is itself gated behind `Auto_Unlock`. Resolution, using only 1-tick failure probes plus 200-tick Hay harvests:

```python
def bootstrap():
    # Blind phase: no Senses, no Costs, no get_cost. Hay is the only currency.
    # Probe the enablers in fixed weight order; each failed unlock is 1 tick.
    # Auto_Unlock is FIRST so that if unlock() is gated, we acquire the gate first.
    enablers = [Unlocks.Auto_Unlock, Unlocks.Senses, Unlocks.Costs]
    while num_unlocked(Unlocks.Costs) == 0:
        if over_budget_blind():        # tick-count guard works pre-Timing too (get_tick_count is always 0-tick)
            return
        harvest()                      # 1x1 grassland auto-grows grass → Hay, no gating needed yet
        for u in enablers:
            if num_unlocked(u) == 0:
                unlock(u)              # 1t if too poor / gated / no prereq; 200t when it lands
```

Notes:
- `Auto_Unlock` is **harmless if not required** — `unlock(Auto_Unlock)` just fails at 1 tick forever and we move on; it's acquired first only if the engine genuinely needs it. This closes the §11② correctness gap that all three candidates left open.
- We don't gate `harvest()` with `can_harvest()` here because `Senses` (which provides `can_harvest`) isn't owned yet — in the blind phase we accept the occasional empty-harvest. The grass regrow is 0.5 s (~200 ticks), so a `harvest()` almost always lands; this is cheaper than not harvesting at all. Once `Senses` lands, all later harvests are `can_harvest()`-gated (§3).
- `get_tick_count()` is **0 ticks and always available** (STRATEGY §1-2) — it does **not** require the `Timing` unlock to *read*; `Timing` gates the richer time API, but the raw tick counter is free from the start. This is what lets the budget guard work even in the blind phase.

### 1.3 `pick_next_unlock()` — weight-ordered, runtime-priced, correctness-safe

**Policy is static (human leverage knowledge); economics is dynamic (runtime `get_cost`).** Each candidate carries a tunable weight `W[U]` (read from `sim_globals`, §4). Weights only **reorder among the affordable** — they can never cause an unaffordable attempt (that would just 1-tick-fail) and never block a cheap successful unlock. So a *wrong* weight costs at most a few 1-tick probes, never correctness (Design 3's key invariant).

```python
def pick_next_unlock():
    best = None
    best_w = -1
    for u in CANDIDATES:                  # see §2 for the seed set + recursive injection
        if num_unlocked(u) > 0 and not upgradable(u):
            continue                      # already owned → skip
        c = get_cost(u)                   # 1 tick; None ⇒ maxed/owned → skip
        if c == None:
            continue
        if affordable(c) and W[u] > best_w:
            best, best_w = u, W[u]
    return best                           # None ⇒ nothing affordable → go farm a bottleneck
```

**Discovering hidden prereqs without a hardcoded edge list:** if `pick_next_unlock()` returns `None` *and* we own every affordable candidate, the binding constraint is either (a) **an item deficit** — handled by `farm_bottleneck()` (§3.1) which reads the top candidate's `get_cost` dict and farms the exact missing item; or (b) **a hidden unlock gate** — surfaced by the per-pass `try_unlock` probes already in the loop (each un-owned candidate gets a 1-tick poke as it becomes affordable). The probe set is **bounded** to the live `CANDIDATES` frontier to avoid a tick tax (judges' minor-flaw note), but that frontier **grows by recursive injection** (§2.2), so an off-seed-list prereq is *not* a permanent blind spot the way it was in Design 1.

### 1.4 The termination guards (the robustness spine)

Two independent guards, both 0–1 tick, guarantee the program **always ends** — the single most important correctness property (a run that never terminates is never scored):

- **Tick budget:** `over_budget(start) = (get_tick_count() - start) > TICK_BUDGET`. `get_tick_count()` is 0 ticks and always available. `TICK_BUDGET` is set generously from `simulate()` measurements (e.g. 3–5× the observed honest-run length) and read from `sim_globals`.
- **No-progress watchdog:** `stalled()` returns `True` if neither `num_unlocked` (summed over `CANDIDATES`) nor the relevant `num_items` has increased for `STALL_LIMIT` consecutive passes. This catches the "permanently-unaffordable prereq / farm Hay forever" hang that Design 1 had no defense against.

Both return cleanly (`return`), ending the program so the partial run is scored rather than hanging.

---

## 2. Unlock prioritization policy (data-driven, force-multipliers cut by default)

### 2.1 The ranking principle and the rationale (early force-multipliers vs critical-path)

**For a single-flag goal funded by single-digit-to-low Hay on a tiny early farm, force-multipliers are CUT by default.** This is the decisive call all three judges endorsed for the speed lens, and the explicit fix for Design 2's fatal flaw.

Rationale, grounded in the tick model:
- Early unlock costs are tiny in Hay (`costs.md`: `get_cost(Unlocks.Loops) → {Items.Hay: 5}`). The critical path is a **handful of 200-tick Hay harvests**.
- Every multiplier costs a **200-tick `unlock`** plus its item cost, and `Megafarm`'s drones each cost a **200-tick `spawn_drone`** (confirmed `__builtins__.py:1212`, 200t/success). `Expand` **resets the farm on every upgrade** (STRATEGY §2), paying the regrow penalty repeatedly.
- A multiplier only pays back if **remaining farming ≫ its cost**. On a few-harvest path it usually does not, so buying it strictly *delays* the flag. Design 3's tie-break "multipliers are strictly dominant when affordable" is **false for a short reset** (judges, robustness + speed), so we do **not** adopt it.

**The one exception worth a conditional look: `Speed`.** It halves wall-clock on *every* remaining 200-tick action, including the Hay harvests that fund the rest of the run. It is the only multiplier that can pay back on a short reset. It is therefore **cut by default but re-enabled iff `simulate()` proves a break-even** (§4) — a single tunable boolean, not an assumption (Design 1 §2.4).

### 2.2 The candidate set and weights (seed + recursive injection)

**Policy:** a single tunable weight vector. Higher `W` = attempted earlier among affordable. **Off-path unlocks have weight 0 and are excluded from the candidate set entirely** — we never farm crops/mazes/dinos/cosmetics we don't need (`leaderboard.md`: *"You do not have to unlock everything"*).

| Tier | Unlock(s) | Default W | Rationale (mechanic-grounded) |
|---|---|---|---|
| Engine enablers | `Auto_Unlock`, `Senses`, `Costs` | 100 | Without `Costs`, `get_cost` is blind; `Senses` gives `num_items`/`can_harvest`/positions; `Auto_Unlock` seeded first per §11②. Cheap, unblock everything. |
| Goal | `Leaderboard` | ∞ (always polled first, §1.1) | The terminal flag. Polled every pass at 1 tick; bought the instant affordable. |
| **Force-multipliers (CUT by default)** | `Megafarm`, `Expand`, `Watering`, `Fertilizer`, `Polyculture` | **0** | Off the single-flag path; each costs 200t + items (+ `spawn_drone` 200t each, + Expand farm-reset). Excluded unless a `Leaderboard` prereq literally gates on one. |
| **Conditional multiplier** | `Speed` | **0 → tuned** | Re-enabled only if `simulate()` proves break-even (§4). The sole multiplier that can pay back on a short reset. |
| Lazy economy | `Plant`, `Grass` | injected | `Plant` injected only when a cost names a planted item (Wood/Carrot); `Grass` only if Hay-yield-per-harvest becomes the bottleneck. |
| Lazy crops | `Carrots`, `Trees`, … | injected | Raised into the set **only** when `get_cost(Leaderboard)` (or a higher candidate) names that crop's item — recursive prereq discovery (§2.3). |

**Recursive prereq injection (fixes Design 1's blind spot):** when a cost dict names item `it`, the engine looks up `crop_for_item(it)` (a runtime map, §3.1); if that crop's unlock isn't owned, it is **injected into `CANDIDATES`** with elevated weight, and *its* `get_cost` is read in turn — so the engine farms toward "the crop-unlock that produces the item that funds the goal," discovering arbitrarily deep chains without any hardcoded edge list.

### 2.3 Tie-breaking

Among affordable candidates, attempt in this order: (1) **`Leaderboard`** (always — §1.1); (2) engine enablers (`Auto_Unlock`/`Senses`/`Costs`); (3) highest `W`; (4) cheapest by Hay-equivalent cost. Note we **deliberately do not** adopt Design 3's "multipliers dominant when affordable" tie-break — it's the speed-killing default the judges rejected.

---

## 3. Per-tier farming subroutines and reuse

One shared library, one parallel primitive, **lazily-built earners**. Every earner shares the same shape: **1-tick sensor gate → 200-tick action → repeat to a target count** (STRATEGY §1-3: gate every 200-tick action with a 1-tick sensor).

### 3.1 `farm_bottleneck()` — fund exactly the deficit (the key anti-waste primitive)

```python
def farm_bottleneck():
    u = top_priority_candidate()          # highest-W un-owned candidate
    cost = get_cost(u)                    # 1 tick
    it = cheapest_missing_item(cost)      # the missing item cheapest to produce now
    if it == None:
        return                            # nothing producible → watchdog will catch a stall
    need = cost[it] - num_items(it)       # farm EXACTLY the deficit, never more (Design 1)
    earn(it, need)
```

`earn(item, n)` dispatches via a **runtime** `crop_for_item` map (Hay←grass, Wood←Bush/Tree, Carrot←Carrot, …), gated by `can_grow` (`num_unlocked(entity) > 0`) so we never plant an unowned entity. **Earners are built lazily** — the Wood/Carrot earner only ever instantiates if a cost dict names Wood/Carrot, so the binary stays minimal (judges: the strongest YAGNI mechanism).

### 3.2 The single auto-scaling primitive `for_all(task)`

One traversal, driven by `max_drones()`/`get_world_size()`, degenerates to single-drone/single-tile on the 1×1 start and auto-scales as `Megafarm`/`Expand`/`Speed` land — **no hardcoded 8** (fixes the repo's stride coverage bug, STRATEGY §10.4):

```python
def for_all(task):
    def row():
        for _ in range(get_world_size() - 1):
            task(); move(East)
        task()
    for _ in range(get_world_size()):
        if not spawn_drone(row):          # 200t success / 1t fail → never over-spawn (STRATEGY §4)
            row()                         # at-limit or 1x1: do it yourself, no column skipped
        move(North)
```

On the actual reset path (single drone, ~1×1 farm) this is just a single in-place `harvest()` loop — but the same code serves the multi-drone era for free **if** a multiplier is ever bought.

### 3.3 Per-tier earners (only the cheap ones the reset can touch)

| Tier | Earner | Mechanic (authoritative) | Built when |
|---|---|---|---|
| 0 (always) | `earn_hay` | grassland auto-grows → `harvest()`; **0.5 s** regrow, free, `can_harvest`-gated (post-Senses) | always (bootstrap currency) |
| 1 (lazy) | `earn_wood` | `plant(Bush)`→`harvest()`; bush avg **4 s**; needs `Plant` | only if a cost names Wood |
| 2 (lazy) | `earn_carrot` | `till`→`plant(Carrot)`; **6 s**, costs wood+hay; needs `Carrots` | only if a cost names Carrot |

Exotic modes (`cactus/pumpkin/sunflower/maze/dino`) are **off-path, weight 0, never imported** by the reset run (import executes the file = wasted ticks, STRATEGY §8.8).

### 3.4 Race discipline (only relevant if a multiplier is ever bought)

If `simulate()` ever proves a multiplier worth buying, the `for_all` partition gives **one drone per row → tile-disjoint ownership**, with water/fertilizer **off by default**. This structurally eliminates the `megafarm.md` `if get_water()<0.5: use_item(Water)` race (which is exactly the repo's `harvest.py` bug, STRATEGY §10.5) rather than patching it. On the default cut path, Megafarm is never bought, so this hazard class is sidestepped entirely.

---

## 4. Offline tuning with `simulate()` (seeded, deterministic)

`simulate(filename, sim_unlocks, sim_items, sim_globals, seed, speedup)` returns **wall-clock seconds**, leaves the real farm untouched, and is **deterministic for a fixed positive seed** (`simulation.md`; confirmed `__builtins__.py:1008`). The `Fastest_Reset` equivalent start is exactly `sim_unlocks={}, sim_items={}, sim_globals={}` (`leaderboard.md`). Lives in **dev-only `tune.py`**, guarded by `if __name__ == "__main__"`; the scored run never calls `simulate()` (it's 200 ticks and pointless mid-run).

**Parametrize, never edit logic:** the engine reads all knobs from `sim_globals` with sane defaults — the weight vector `W`, `BUY_SPEED` (bool), `TICK_BUDGET`, `STALL_LIMIT`, and `BATCH` granularity. Tuning changes only numbers.

**Protocol:**
1. **Reveal the true DAG/cost table once, for pruning.** A first `simulate()` run with `quick_print()` (0 ticks) logging each `get_cost(Leaderboard)` and candidate result reveals the real prereq chain and costs. Use this to **prune** `CANDIDATES` to the genuinely on-path set — **never to hardcode** prices into the shipped loop (which stays robust via runtime `get_cost`). Also confirms whether `unlock()` is gated behind `Auto_Unlock` (§11②) directly from the game.
2. **Decide the one ambiguous policy knob:** sweep `BUY_SPEED ∈ {0,1}`; whichever yields lower **mean** seconds across a fixed seed set `{1,2,3,4,5}` sets the constant. (Average over seeds because growth times are per-seed random and the real leaderboard averages over ≥2 hours.)
3. **Set the safety budgets:** measure honest-run length, set `TICK_BUDGET` to a generous multiple, set `STALL_LIMIT` above the worst observed no-progress streak.
4. **Tune `BATCH`** (how much to over-farm per cycle to amortize poll overhead) by sweeping and minimizing mean seconds.
5. **Validate termination + finish** with the exact start state, confirming the program ends with `num_unlocked(Unlocks.Leaderboard) > 0`, before uploading via `leaderboard_run(Leaderboards.Fastest_Reset, "reset_main", speedup)`.

Coordinate-descent the weights from the §2.2 seeds; `speedup` (e.g. 64–256) only compresses wait time, not the result.

---

## 5. Risk handling

| Risk | Mitigation (mechanic-grounded) |
|---|---|
| **Cost table & DAG edges not in files** (§2, §11) | Never hardcoded. `get_cost()` prices live; `unlock()`-failure (1 tick) probes edges; `pick_next_unlock` is a runtime weight-ordered closure search; `simulate()` reveals the table only for *pruning*. |
| **Chicken-and-egg (need Costs to price Costs)** | `bootstrap()` blind-polls `unlock(Senses)`/`unlock(Costs)` at 1 tick/fail while harvesting Hay — no pricing needed to buy them. |
| **🔴 Non-termination under unverified Auto_Unlock gate (§11②)** — the one correctness-fatal flaw | (a) `Auto_Unlock` seeded **first** in `bootstrap()` so the gate is acquired if required; (b) **0-tick `get_tick_count()` budget guard** returns cleanly so the run is *always* scored even if the gate scenario is worse than expected. (Graft from Design 3.) |
| **Unbounded "farm forever" hang** (Design 1's hole) | No-progress watchdog `stalled()` + tick budget both `return` cleanly. |
| **Off-seed-list hidden prereq** (Design 1's blind spot) | Recursive prereq injection (§2.2): cost-named items pull their producing crop's unlock (and its prereqs) into the live frontier. |
| **A required prereq is far pricier than assumed** (the dominant *time* risk) | `farm_bottleneck` funds **exactly** the deficit via the cheapest item the cost dict permits; lazy earners add only the crop code that exact cost demands; `simulate()` pre-measures the true cost so there are no scored-run surprises. This is the run's irreducible cost — the design pays it minimally, it cannot make it cheaper. |
| **Termination at the goal** (`leaderboard.md`) | Loop exits the instant the flag flips; no trailing work; `return` on a successful `try_unlock(TARGET)`. |
| **Single-plot early game / single vs multi-drone** | One `for_all` primitive degenerates to single-drone/single-tile on 1×1; no separate early-game code path. Megafarm cut by default → typically stays single-drone. |
| **Race conditions post-Megafarm** | Sidestepped by default (Megafarm not bought). If ever bought: tile-disjoint one-drone-per-row partition + water/fertilizer off → race structurally eliminated. |
| **Over-investing in multipliers** (Design 2's flaw) | All multipliers weight 0 (cut); only `Speed` is conditionally re-enabled on a proven `simulate()` break-even. |
| **`print()` trap (~400 ticks, speed-immune)** | Forbidden. Debug via `quick_print()`/`get_tick_count()` (0 ticks). |
| **`harvest()` destroys-and-still-200-ticks** | Every post-Senses `harvest()` gated by `can_harvest()` (1 tick). |
| **`def`-in-loop / import-executes-file** | All worker `def`s hoisted to module top; exotic modes never imported by the reset run. |
| **Per-pass probe tick tax** | Probe set bounded to the live `CANDIDATES` frontier; cost is a few 1-tick polls per pass, negligible. |

---

## 6. Mapping to the current repo (keep / refactor / discard)

The repo is built for the *throughput* leaderboards and has **no purchase logic at all** (STRATEGY §10.1) — `main.py`'s `while True` never terminates (fatal for the reset) and routes between crop modes by lowest inventory. Almost all of it is off the reset critical path.

| File | Verdict | Reason |
|---|---|---|
| `main.py` | **Discard / rewrite** | `while True` never terminates (fatal — `leaderboard.md` requires the program to end); hardcoded-8 stride coverage bug (§10.4). Replaced by `reset_main.py` (§1). |
| `v2.py` | **Discard (reset)** | `find_lowest_item` crashes on count ties via `min()`-on-Item (§10.2) and routes Gold/Bone into unready/destructive modes. Bottleneck detection (§3.1) is cost-driven, not inventory-min-driven. |
| `harvest.py` | **Refactor → shrink** | Keep only the `can_harvest()→harvest()` gate idea. **Remove** the race-prone water logic (§10.5 = the `megafarm.md` anti-pattern), the unconditional fertilizer-on-fast-crops, and the accidental Weird_Substance infection toggle. Collapses into `earn_hay`. |
| `plant.py` | **Refactor → lazy earners** | Keep bush/carrot planting **gated by `num_unlocked(entity)`** and routed through `crop_for_item`; drop the checkerboard-tree / pumpkin / sunflower / cactus branches (off-path). |
| `set_ground_type.py` | **Keep (tiny)** | `toSoil`/`toGrassland` via `till()` toggle is correct; reused inside `earn_wood`/`earn_carrot` only if ever needed. |
| `moves.py` | **Keep minimal** | `to(x,y)` toroidal mover reusable by `for_all`; but on a 1×1 farm `move()` isn't even unlocked, so it's dormant by default. Drop big-farm throughput helpers from the reset import graph. |
| `cactus_mode.py`, `pumpkin_mode.py`, `sunflower_mode.py`, `maze_mode.py`, `dino_mode.py` | **Discard from reset path** | All are *yield* features for other leaderboards (weight 0, off-path), each with known defects (§10.3/§6/§10.5–10.7); `maze_mode` calls `clear()` wiping the whole farm — actively dangerous. **Not imported** by the reset run (import = executed ticks). Keep the files on a branch for their own leaderboards. |
| `game_notes.py` | **Discard** | Superseded by STRATEGY.md (its errors tabulated in §9). |
| `__builtins__.py` | **Keep as reference only** | API stub; out-of-date local copy. Trust in-game docs + STRATEGY.md over it. |
| `STRATEGY.md` | **Keep** | Authoritative foundation. |

**New files:** `farmlib.py` (`bootstrap`, `for_all`, `earn`/lazy earners, `crop_for_item`, `farm_bottleneck`, `pick_next_unlock`, `try_unlock`, `affordable`, `over_budget`, `stalled`), `reset_main.py` (the §1.1 loop + `run()`), and dev-only `tune.py` (the `simulate()` sweeps, `__main__`-guarded). **Three small modules replace nine brittle files.**

---

## 7. Incremental, atomic implementation roadmap

Each milestone is independently testable via seeded `simulate()` and leaves the system in a working state.

| # | Milestone | Atomic deliverable | How to test (via `simulate()`) |
|---|---|---|---|
| **M0** | **Probe harness** | `tune.py` that runs `simulate("reset_main", {}, {}, {}, seed, 64)` against a trivial `reset_main.py` whose `run()` only blind-harvests Hay and `quick_print()`s `get_tick_count()`. | Confirm `simulate` runs deterministically (same seed → same seconds). Establishes the offline loop before any logic exists. |
| **M1** | **Bootstrap + terminate** | `farmlib.bootstrap()` (blind-poll `Auto_Unlock`→`Senses`→`Costs` while harvesting Hay) + `over_budget`/`stalled` guards + a `run()` that exits on budget. | `simulate` from the empty start; confirm `Costs` unlocks (or the budget guard returns cleanly if the Auto_Unlock gate exists). **Validates §11② defense first** — the highest-risk item. |
| **M2** | **Goal-polling loop** | Add the `while num_unlocked(TARGET)==0` loop with goal-first `try_unlock(TARGET)` and the termination guards. No buying yet. | `simulate`; confirm the program **always terminates** (via guard) and logs `get_cost(Leaderboard)` once `Costs` is up — revealing the true prereq chain. |
| **M3** | **Priced greedy buying** | `pick_next_unlock` (weight-ordered, affordable-only) + `try_unlock(nxt)` + `affordable`. Weights from `sim_globals`, multipliers at 0. | `simulate`; confirm it buys the cheap enablers and any cheap on-path nodes, still terminating. |
| **M4** | **Bottleneck farming + lazy earners** | `farm_bottleneck` (exact-deficit), `crop_for_item`, `earn_hay`, and lazily `earn_wood`/`earn_carrot` if M2's log showed those items in `get_cost(Leaderboard)`. Recursive prereq injection. | `simulate`; confirm it reaches `num_unlocked(Leaderboard) > 0` and terminates. **This is the first end-to-end win.** |
| **M5** | **`for_all` auto-scaling primitive** | Replace the single-tile harvest loop with `for_all(task)`. No behavior change at 1×1; future-proofs for any multiplier. | `simulate`; confirm identical result at 1×1 (degenerates correctly), and correct coverage if `sim_unlocks` is seeded with `Expand`/`Megafarm`. |
| **M6** | **Offline tuning sweep** | `tune.py` sweeps `W`, `BUY_SPEED`, `TICK_BUDGET`, `STALL_LIMIT`, `BATCH` across seeds `{1..5}`; pick the mean-minimizing config; prune `CANDIDATES` to the revealed on-path set. | Compare mean seconds across configs; lock the winning constants. **Decides the one ambiguous knob (Speed) empirically.** |
| **M7** | **Upload** | `leaderboard_run(Leaderboards.Fastest_Reset, "reset_main", speedup)` with tuned constants. | Final scored run; the program terminates the instant the flag flips. |

Order rationale: **M1 validates the dominant catastrophic risk (non-termination / Auto_Unlock gate) before any economic logic exists**, so a fatal-flaw discovery is cheap. Each subsequent milestone adds exactly one capability, independently `simulate()`-verifiable, with the system terminating-and-scorable at every step from M1 onward.

---

### Relevant files
- Authoritative: `/Users/dion/Desktop/toy/the-farmer-was-replaced/STRATEGY.md`
- Builtins reference (signatures/tick costs): `/Users/dion/Desktop/toy/the-farmer-was-replaced/__builtins__.py` (`get_cost` L865, `unlock` L927, `num_unlocked` L944, `simulate` L1008, `spawn_drone` L1212, `max_drones` L1278, `get_tick_count` L690)
- New (to add): `/Users/dion/Desktop/toy/the-farmer-was-replaced/{reset_main.py, farmlib.py, tune.py}`
- Discard/refactor for the reset run: `/Users/dion/Desktop/toy/the-farmer-was-replaced/{main.py, v2.py, harvest.py, plant.py, moves.py, set_ground_type.py, cactus_mode.py, pumpkin_mode.py, sunflower_mode.py, maze_mode.py, dino_mode.py, game_notes.py}`