# clauding playthrough - Stage 16: parallel engine v3 (Megafarm drones)
# ASCII-only comments (in-game editor breaks on non-ASCII).
#
# Megafarm is unlocked, so farming is now parallel: one drone per row, auto-
# scaling with max_drones(). Each drone works its own row, so no two drones
# touch the same tile (no race conditions). The engine also auto-buys Megafarm
# and Speed upgrades from surplus to compound drones x speed.
#
# Progression chain unchanged: fertilized pumpkin -> weird_substance -> maze ->
# gold -> unlocks. Priority = scarcest-resource-first (worst_item).

WOOD_MIN = 20
CARROT_HIGH = 250

def water_if_dry():
    if num_items(Items.Water) > 0 and get_water() < 0.5:
        use_item(Items.Water)

# ---------- parallel helper: one drone per row ----------
def parallel_rows(row_fn):
    size = get_world_size()
    drones = []
    for i in range(size):
        d = spawn_drone(row_fn)
        if d:
            drones.append(d)
        else:
            row_fn()                 # no drone free -> do this row myself
        move(North)
    for d in drones:
        wait_for(d)

# ---------- balanced farm (carrot / wood / hay) ----------
def balanced_tile():
    if can_harvest():
        harvest()
    k = (get_pos_x() + get_pos_y()) % 3
    if k == 1:
        if not plant(Entities.Tree):
            plant(Entities.Bush)
        water_if_dry()
    elif k == 0:
        if get_ground_type() == Grounds.Grassland:
            till()
        if num_items(Items.Wood) > WOOD_MIN:
            plant(Entities.Carrot)
        water_if_dry()
    else:
        if get_ground_type() == Grounds.Soil:
            till()

def balanced_row():
    size = get_world_size()
    for i in range(size):
        balanced_tile()
        move(East)

def balanced_sweep():
    parallel_rows(balanced_row)

# ---------- mega-pumpkin (parallel rows, fertilizer in place) ----------
def pumpkin_row():
    # re-walk this row until every tile is a grown pumpkin. Fertilizer matures
    # in place (and makes weird_substance); without it, growth happens between
    # passes as the drone traverses, so it still converges.
    size = get_world_size()
    done = False
    while not done:
        done = True
        for i in range(size):
            if get_ground_type() == Grounds.Grassland:
                till()
            e = get_entity_type()
            if e == Entities.Pumpkin and can_harvest():
                pass
            else:
                done = False
                if e == None or e == Entities.Dead_Pumpkin:
                    if not plant(Entities.Pumpkin):
                        return            # out of carrots -> stop this row
                if num_items(Items.Fertilizer) > 0:
                    use_item(Items.Fertilizer)
            move(East)

def pumpkin_mega_once():
    clear()
    parallel_rows(pumpkin_row)        # every row -> grown pumpkins -> merged mega
    harvest()                         # collect the mega (drone is back at 0,0)

def pumpkin_batch():
    if num_items(Items.Carrot) < CARROT_HIGH:
        tries = 0
        while num_items(Items.Carrot) < CARROT_HIGH and tries < 40:
            balanced_sweep()
            tries = tries + 1
    pumpkin_mega_once()

# ---------- maze -> gold (single drone) ----------
def maze_substance_need():
    return get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)

def make_maze():
    if num_items(Items.Weird_Substance) < maze_substance_need():
        return False
    clear()
    plant(Entities.Bush)
    while not can_harvest():
        if num_items(Items.Fertilizer) > 0:
            use_item(Items.Fertilizer)
    use_item(Items.Weird_Substance, maze_substance_need())
    return True

def solve_maze():
    dirs = [North, East, South, West]
    facing = 0
    while get_entity_type() != Entities.Treasure:
        right = (facing + 1) % 4
        if can_move(dirs[right]):
            facing = right
            move(dirs[facing])
        elif can_move(dirs[facing]):
            move(dirs[facing])
        else:
            left = (facing + 3) % 4
            if can_move(dirs[left]):
                facing = left
                move(dirs[facing])
            else:
                facing = (facing + 2) % 4
                move(dirs[facing])
    harvest()

def maze_run():
    if make_maze():
        solve_maze()

# ---------- producer: scarcest-first ----------
def produce(item):
    if item == Items.Gold:
        if num_items(Items.Weird_Substance) < maze_substance_need():
            pumpkin_batch()
        else:
            maze_run()
        return True
    if item == Items.Weird_Substance or item == Items.Pumpkin:
        pumpkin_batch()
        return True
    if item == Items.Hay or item == Items.Wood or item == Items.Carrot:
        balanced_sweep()
        return True
    return False

def affordable(cost):
    for item in cost:
        if num_items(item) < cost[item]:
            return False
    return True

def worst_item(cost):
    worst = None
    worst_def = 0
    for item in cost:
        d = cost[item] - num_items(item)
        if d > worst_def:
            worst_def = d
            worst = item
    return worst

# buy compounding upgrades whenever surplus already covers them
def buy_upgrades():
    ups = [Unlocks.Megafarm, Unlocks.Speed]
    for u in ups:
        cost = get_cost(u)
        if cost != None and affordable(cost):
            unlock(u)

def target_list():
    return [Unlocks.Simulation, Unlocks.Dinosaurs, Unlocks.Leaderboard]

def run():
    blocked = set()
    while True:
        buy_upgrades()
        target = None
        for t in target_list():
            if num_unlocked(t) == 0 and get_cost(t) != None and not (t in blocked):
                target = t
                break
        if target == None:
            balanced_sweep()
            blocked = set()
            continue
        cost = get_cost(target)
        if affordable(cost):
            if not unlock(target):
                blocked.add(target)
        else:
            item = worst_item(cost)
            if not produce(item):
                blocked.add(target)

run()
