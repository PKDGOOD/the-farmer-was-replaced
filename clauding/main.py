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
BONE_CACTUS_MIN = 2000
BONE_APPLES = 80
AUTO_BONE = False
WEIRD_MAZE_BUFFER = 12

def water_if_dry():
    if num_items(Items.Water) > 0 and get_water() < 0.5:
        use_item(Items.Water)

# True if we can pay the planting cost of entity (avoids failed-plant warnings)
def afford_plant(entity):
    c = get_cost(entity)
    if c == None:
        return True
    for item in c:
        if num_items(item) < c[item]:
            return False
    return True

def afford_plant_many(entity, n):
    c = get_cost(entity)
    if c == None:
        return True
    for item in c:
        if num_items(item) < c[item] * n:
            return False
    return True

def weird_abundant():
    if num_unlocked(Unlocks.Mazes) == 0:
        return False
    need = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    return num_items(Items.Weird_Substance) >= need * WEIRD_MAZE_BUFFER

# ---------- parallel helper: split rows/cols across available drones ----------
def return_to_x(start_x):
    size = get_world_size()
    east = (start_x - get_pos_x() + size) % size
    west = (get_pos_x() - start_x + size) % size
    if east < west:
        for i in range(east):
            move(East)
    else:
        for i in range(west):
            move(West)

def return_to_y(start_y):
    size = get_world_size()
    north = (start_y - get_pos_y() + size) % size
    south = (get_pos_y() - start_y + size) % size
    if north < south:
        for i in range(north):
            move(North)
    else:
        for i in range(south):
            move(South)

def move_north_n(n):
    for i in range(n):
        move(North)

def move_east_n(n):
    for i in range(n):
        move(East)

def row_worker(row_fn, start, stride):
    size = get_world_size()
    start_x = get_pos_x()
    row = start
    while row < size:
        row_fn()
        row = row + stride
        if row < size:
            return_to_x(start_x)
            move_north_n(stride)

def row_worker_arg(row_fn, arg, start, stride):
    size = get_world_size()
    start_x = get_pos_x()
    row = start
    while row < size:
        row_fn(arg)
        row = row + stride
        if row < size:
            return_to_x(start_x)
            move_north_n(stride)

def col_worker(col_fn, start, stride):
    size = get_world_size()
    start_y = get_pos_y()
    col = start
    while col < size:
        col_fn()
        col = col + stride
        if col < size:
            return_to_y(start_y)
            move_east_n(stride)

def parallel_rows(row_fn):
    size = get_world_size()
    workers = max_drones()
    if workers < 1:
        workers = 1
    if workers > size:
        workers = size
    drones = []
    origin_x = get_pos_x()
    origin_y = get_pos_y()
    for i in range(workers - 1):
        d = spawn_drone(row_worker, row_fn, i, workers)
        if d:
            drones.append(d)
        else:
            start_x = get_pos_x()
            start_y = get_pos_y()
            row_worker(row_fn, i, workers)
            return_to_x(start_x)
            return_to_y(start_y)
        move(North)
    row_worker(row_fn, workers - 1, workers)
    return_to_x(origin_x)
    return_to_y(origin_y)
    for d in drones:
        wait_for(d)

# one drone per column (spawn along the bottom row, moving East)
def parallel_cols(col_fn):
    size = get_world_size()
    workers = max_drones()
    if workers < 1:
        workers = 1
    if workers > size:
        workers = size
    drones = []
    origin_x = get_pos_x()
    origin_y = get_pos_y()
    for i in range(workers - 1):
        d = spawn_drone(col_worker, col_fn, i, workers)
        if d:
            drones.append(d)
        else:
            start_x = get_pos_x()
            start_y = get_pos_y()
            col_worker(col_fn, i, workers)
            return_to_x(start_x)
            return_to_y(start_y)
        move(East)
    col_worker(col_fn, workers - 1, workers)
    return_to_x(origin_x)
    return_to_y(origin_y)
    for d in drones:
        wait_for(d)

# one drone per row, forwarding a single arg to each (snapshotted, no closure)
def parallel_rows_arg(row_fn, arg):
    size = get_world_size()
    workers = max_drones()
    if workers < 1:
        workers = 1
    if workers > size:
        workers = size
    drones = []
    origin_x = get_pos_x()
    origin_y = get_pos_y()
    for i in range(workers - 1):
        d = spawn_drone(row_worker_arg, row_fn, arg, i, workers)
        if d:
            drones.append(d)
        else:
            start_x = get_pos_x()
            start_y = get_pos_y()
            row_worker_arg(row_fn, arg, i, workers)
            return_to_x(start_x)
            return_to_y(start_y)
        move(North)
    row_worker_arg(row_fn, arg, workers - 1, workers)
    return_to_x(origin_x)
    return_to_y(origin_y)
    for d in drones:
        wait_for(d)

def grass_tile():
    if get_ground_type() == Grounds.Soil:
        till()

def plant_entity_safe(entity):
    if entity == Entities.Grass:
        if get_entity_type() == None and get_ground_type() == Grounds.Soil:
            till()
        return True
    if entity == Entities.Carrot:
        if not afford_plant_many(Entities.Carrot, get_world_size()):
            return False
        if get_ground_type() == Grounds.Grassland:
            till()
        if get_entity_type() == None:
            return plant(Entities.Carrot)
        return False
    if entity == Entities.Tree:
        if get_entity_type() == None and afford_plant_many(Entities.Tree, get_world_size()):
            return plant(Entities.Tree)
        return False
    if entity == Entities.Bush:
        if get_entity_type() == None and afford_plant_many(Entities.Bush, get_world_size()):
            return plant(Entities.Bush)
        return False
    return False

def move_east_n(n):
    for i in range(n):
        move(East)

def move_west_n(n):
    for i in range(n):
        move(West)

def companion_same_row():
    comp = get_companion()
    if comp == None:
        return
    entity, pos = comp
    tx, ty = pos
    x = get_pos_x()
    y = get_pos_y()
    if ty != y:
        return
    dx = tx - x
    if dx > 0 and dx <= 3:
        move_east_n(dx)
        plant_entity_safe(entity)
        move_west_n(dx)
    elif dx < 0 and dx >= -3:
        move_west_n(-dx)
        plant_entity_safe(entity)
        move_east_n(-dx)

def plant_wood():
    size = get_world_size()
    if (get_pos_x() + get_pos_y()) % 2 == 0 and afford_plant_many(Entities.Tree, size):
        if plant(Entities.Tree):
            companion_same_row()
            return True
    if afford_plant_many(Entities.Bush, size):
        if plant(Entities.Bush):
            companion_same_row()
            return True
    return False

# ---------- basic farm (targeted hay / wood / carrot) ----------
def basic_tile(target):
    if can_harvest():
        harvest()
    if target == Items.Hay:
        grass_tile()
        return
    if target == Items.Wood:
        if get_entity_type() == None:
            plant_wood()
            water_if_dry()
        return
    if target == Items.Carrot:
        if not afford_plant_many(Entities.Carrot, get_world_size()):
            grass_tile()
            return
        if get_ground_type() == Grounds.Grassland:
            till()
        if get_entity_type() == None:
            if plant(Entities.Carrot):
                companion_same_row()
        water_if_dry()

def basic_row(target):
    size = get_world_size()
    for i in range(size - 1):
        basic_tile(target)
        move(East)
    basic_tile(target)

def basic_sweep(target):
    parallel_rows_arg(basic_row, target)

# ---------- dinosaur -> bone ----------
def dino_step_toward(tx, ty):
    if get_pos_x() < tx and move(East):
        return True
    if get_pos_x() > tx and move(West):
        return True
    if get_pos_y() < ty and move(North):
        return True
    if get_pos_y() > ty and move(South):
        return True
    if move(North):
        return True
    if move(East):
        return True
    if move(South):
        return True
    if move(West):
        return True
    return False

def bone_run():
    if num_items(Items.Cactus) < BONE_CACTUS_MIN:
        cactus_once()
        return
    clear()
    change_hat(Hats.Dinosaur_Hat)
    apples = 0
    tries = 0
    while apples < BONE_APPLES and tries < BONE_APPLES * 80:
        pos = measure()
        if pos == None:
            break
        tx, ty = pos
        if get_pos_x() == tx and get_pos_y() == ty:
            if not dino_step_toward(tx, ty):
                break
            apples = apples + 1
        else:
            if dino_step_toward(tx, ty):
                if get_pos_x() == tx and get_pos_y() == ty:
                    apples = apples + 1
            else:
                break
        tries = tries + 1
    change_hat(Hats.Gray_Hat)

# ---------- mega-pumpkin (parallel rows, fertilizer in place) ----------
def pumpkin_row():
    # re-walk this row until every tile is a grown pumpkin. Fertilizer matures
    # in place (and makes weird_substance); without it, growth happens between
    # passes as the drone traverses, so it still converges.
    size = get_world_size()
    done = False
    passes = 0
    while not done and passes < 40:
        passes = passes + 1
        done = True
        for i in range(size - 1):
            if get_ground_type() == Grounds.Grassland:
                till()
            e = get_entity_type()
            if e == Entities.Pumpkin and can_harvest():
                pass
            else:
                done = False
                if e == None or e == Entities.Dead_Pumpkin:
                    if not afford_plant_many(Entities.Pumpkin, size):
                        return
                    if not plant(Entities.Pumpkin):
                        return            # out of carrots -> stop this row
                if num_items(Items.Fertilizer) > 0 and not weird_abundant():
                    use_item(Items.Fertilizer)
            move(East)
        if get_ground_type() == Grounds.Grassland:
            till()
        e = get_entity_type()
        if e == Entities.Pumpkin and can_harvest():
            pass
        else:
            done = False
            if e == None or e == Entities.Dead_Pumpkin:
                if not afford_plant_many(Entities.Pumpkin, size):
                    return
                if not plant(Entities.Pumpkin):
                    return
            if num_items(Items.Fertilizer) > 0 and not weird_abundant():
                use_item(Items.Fertilizer)

def pumpkin_mega_once():
    clear()
    parallel_rows(pumpkin_row)        # every row -> grown pumpkins -> merged mega
    harvest()                         # collect the mega (drone is back at 0,0)

def pumpkin_batch():
    if num_items(Items.Carrot) < CARROT_HIGH:
        tries = 0
        while num_items(Items.Carrot) < CARROT_HIGH and tries < 40:
            basic_sweep(Items.Carrot)
            tries = tries + 1
    pumpkin_mega_once()

# ---------- cactus: sort the grid, harvest cascades (size^2)^2 ----------
# Row-sort ascending East, then column-sort ascending North. Sorting rows then
# columns leaves the rows sorted too, so the whole grid ends up sorted and one
# harvest cascades over every cactus. Both sort phases run one drone per line.
def cactus_plant_row():
    size = get_world_size()
    for i in range(size - 1):
        if can_harvest():
            harvest()                    # clear grown grass so the tile is empty
        if get_ground_type() == Grounds.Grassland:
            till()                        # soil -> grass cannot regrow here
        if get_entity_type() == None and afford_plant_many(Entities.Cactus, size):
            plant(Entities.Cactus)        # only plant when we can pay the cost
        if num_items(Items.Water) > 0 and get_water() < 0.8:
            use_item(Items.Water)
        move(East)
    if can_harvest():
        harvest()
    if get_ground_type() == Grounds.Grassland:
        till()
    if get_entity_type() == None and afford_plant_many(Entities.Cactus, size):
        plant(Entities.Cactus)
    if num_items(Items.Water) > 0 and get_water() < 0.8:
        use_item(Items.Water)

def sort_row():
    size = get_world_size()
    start_x = get_pos_x()
    left = 0
    right = size - 1
    while left < right:
        swapped = False
        for i in range(right - left):
            a = measure()
            b = measure(East)
            if a != None and b != None and a > b:   # guard: skip non-cactus
                swap(East)
                swapped = True
            move(East)

        right = right - 1
        for i in range(right - left + 1):
            a = measure(West)
            b = measure()
            if a != None and b != None and a > b:
                swap(West)
                swapped = True
            move(West)

        left = left + 1
        if not swapped or left >= right:
            break
        move(East)
    return_to_x(start_x)

def sort_col():
    size = get_world_size()
    start_y = get_pos_y()
    bottom = 0
    top = size - 1
    while bottom < top:
        swapped = False
        for i in range(top - bottom):
            a = measure()
            b = measure(North)
            if a != None and b != None and a > b:
                swap(North)
                swapped = True
            move(North)

        top = top - 1
        for i in range(top - bottom + 1):
            a = measure(South)
            b = measure()
            if a != None and b != None and a > b:
                swap(South)
                swapped = True
            move(South)

        bottom = bottom + 1
        if not swapped or bottom >= top:
            break
        move(North)
    return_to_y(start_y)

def cactus_once():
    clear()
    parallel_rows(cactus_plant_row)
    parallel_rows(sort_row)
    parallel_cols(sort_col)
    if get_entity_type() == None:         # (0,0) empty (couldn't afford) -> no hang
        return
    tries = 0
    while not can_harvest() and tries < 3000:   # bounded grow-wait
        if num_items(Items.Fertilizer) > 0:
            use_item(Items.Fertilizer)
        tries = tries + 1
    if can_harvest():
        harvest()                         # sorted + grown -> full cascade

# ---------- sunflowers -> power (8x max-petal) -> global 2x speed ----------
POWER_FLOOR = 250
POWER_TARGET = 700
POWER_ROUNDS = 4
POWER_MIN_ROUND_GAIN = 40

def sun_plant_row():
    size = get_world_size()
    for i in range(size - 1):
        if get_ground_type() == Grounds.Grassland:
            till()
        if get_entity_type() == None and afford_plant_many(Entities.Sunflower, size):
            plant(Entities.Sunflower)
        if num_items(Items.Water) > 0 and get_water() < 0.8:
            use_item(Items.Water)
        move(East)
    if get_ground_type() == Grounds.Grassland:
        till()
    if get_entity_type() == None and afford_plant_many(Entities.Sunflower, size):
        plant(Entities.Sunflower)
    if num_items(Items.Water) > 0 and get_water() < 0.8:
        use_item(Items.Water)

def row_max_petals():                     # parallel-reduction worker: returns row max
    size = get_world_size()
    m = 0
    for i in range(size - 1):
        if can_harvest():
            p = measure()
            if p != None and p > m:
                m = p
        move(East)
    if can_harvest():
        p = measure()
        if p != None and p > m:
            m = p
    return m

def field_max_petals():
    size = get_world_size()
    drones = []
    m = 0
    for i in range(size):
        d = spawn_drone(row_max_petals)
        if d:
            drones.append(d)
        else:
            r = row_max_petals()
            if r > m:
                m = r
        move(North)
    for d in drones:
        r = wait_for(d)
        if r > m:
            m = r
    return m

def harvest_max_row(m):                   # harvest only grown sunflowers at the field max
    size = get_world_size()
    for i in range(size - 1):
        if can_harvest() and measure() == m:
            harvest()                     # 8x power (m is max; the rest stay -> >=10)
            if afford_plant_many(Entities.Sunflower, size):
                plant(Entities.Sunflower)
        move(East)
    if can_harvest() and measure() == m:
        harvest()
        if afford_plant_many(Entities.Sunflower, size):
            plant(Entities.Sunflower)

def power_gen():
    clear()
    parallel_rows(sun_plant_row)          # whole field of sunflowers + watered
    r = 0
    while r < POWER_ROUNDS:
        if num_items(Items.Power) >= POWER_TARGET:
            break
        before = num_items(Items.Power)
        m = field_max_petals()
        if m > 0:
            parallel_rows_arg(harvest_max_row, m)
        after = num_items(Items.Power)
        if after - before < POWER_MIN_ROUND_GAIN:
            break
        r = r + 1

# ---------- maze -> gold (single drone) ----------
def maze_substance_need():
    return get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)

def make_maze():
    need = maze_substance_need()
    if num_items(Items.Weird_Substance) < need:
        return False
    clear()
    if not plant(Entities.Bush):
        return False
    if num_items(Items.Fertilizer) >= 3:
        use_item(Items.Fertilizer, 3)     # batch-mature the bush (4s grow)
    tries = 0
    while not can_harvest() and tries < 3000:
        tries = tries + 1
    return use_item(Items.Weird_Substance, need)   # True iff the maze was created

def maze_key(x, y):
    return x * get_world_size() + y

def seen_key(keys, key):
    for k in keys:
        if k == key:
            return True
    return False

def step_x(x, d):
    size = get_world_size()
    if d == 1:
        return (x + 1) % size
    if d == 3:
        return (x + size - 1) % size
    return x

def step_y(y, d):
    size = get_world_size()
    if d == 0:
        return (y + 1) % size
    if d == 2:
        return (y + size - 1) % size
    return y

def wrap_dist(a, b):
    size = get_world_size()
    d = abs(a - b)
    w = size - d
    if w < d:
        return w
    return d

def maze_dist(x, y, tx, ty):
    return wrap_dist(x, tx) + wrap_dist(y, ty)

def dir_bias(d, prefer_dir):
    b = abs(d - prefer_dir)
    if b > 2:
        return 4 - b
    return b

def choose_maze_dir(tx, ty, seen, prefer_dir):
    dirs = [North, East, South, West]
    x = get_pos_x()
    y = get_pos_y()
    best = -1
    best_d = 1000000
    best_b = 1000000
    for d in range(4):
        if can_move(dirs[d]):
            nx = step_x(x, d)
            ny = step_y(y, d)
            key = maze_key(nx, ny)
            if not seen_key(seen, key):
                md = maze_dist(nx, ny, tx, ty)
                db = dir_bias(d, prefer_dir)
                if best == -1 or md < best_d or (md == best_d and db < best_b):
                    best = d
                    best_d = md
                    best_b = db
    return best

def guided_searcher(first_dir, prefer_dir):
    target = measure()
    if target == None:
        return False
    tx, ty = target
    dirs = [North, East, South, West]
    gold_before = num_items(Items.Gold)
    seen = []
    stack = []
    steps = 0
    limit = get_world_size() * get_world_size() * 8
    start_key = maze_key(get_pos_x(), get_pos_y())
    if get_entity_type() == Entities.Treasure:
        harvest()
        return True
    if first_dir != -1:
        if can_move(dirs[first_dir]):
            seen.append(start_key)
            stack.append(first_dir)
            move(dirs[first_dir])
            steps = steps + 1
        else:
            return False
    while get_entity_type() != Entities.Treasure and steps < limit:
        if num_items(Items.Gold) > gold_before:
            return True
        key = maze_key(get_pos_x(), get_pos_y())
        if first_dir != -1 and key == start_key and len(stack) == 0:
            return False
        if not seen_key(seen, key):
            seen.append(key)
        d = choose_maze_dir(tx, ty, seen, prefer_dir)
        if d != -1:
            stack.append(d)
            move(dirs[d])
        elif len(stack) > 0:
            back = (stack.pop() + 2) % 4
            if can_move(dirs[back]):
                move(dirs[back])
            else:
                return False
        else:
            return False
        steps = steps + 1
    if num_items(Items.Gold) > gold_before:
        return True
    if get_entity_type() == Entities.Treasure:
        harvest()
        return True
    return False

# one wall-following searcher; args passed via spawn_drone (no closures).
# Stops early if another drone already grabbed the treasure (gold went up).
def searcher(start_dir, use_right_hand):
    dirs = [North, East, South, West]
    facing = start_dir
    gold_before = num_items(Items.Gold)
    steps = 0
    limit = get_world_size() * get_world_size() * 8
    while get_entity_type() != Entities.Treasure:
        if num_items(Items.Gold) > gold_before:
            return
        if steps > limit:                 # give up -> never hang the wait_for join
            return
        steps = steps + 1
        right = (facing + 1) % 4
        left = (facing + 3) % 4
        if use_right_hand:
            if can_move(dirs[right]):
                facing = right
            elif can_move(dirs[facing]):
                pass
            elif can_move(dirs[left]):
                facing = left
            else:
                facing = (facing + 2) % 4
        else:
            if can_move(dirs[left]):
                facing = left
            elif can_move(dirs[facing]):
                pass
            elif can_move(dirs[right]):
                facing = right
            else:
                facing = (facing + 2) % 4
        move(dirs[facing])
    harvest()

def maze_run():
    if not make_maze():
        return
    # Split only when the entrance has real branches. If there is just one way
    # in, spawning a helper only adds 200 ticks and leaves the caller waiting.
    drones = []
    gold_before = num_items(Items.Gold)
    dirs = [North, East, South, West]
    branches = []
    for di in range(4):
        if can_move(dirs[di]):
            branches.append(di)
    if len(branches) == 0:
        guided_searcher(-1, 0)
        return
    if len(branches) == 1:
        guided_searcher(branches[0], branches[0])
        return
    last = len(branches) - 1
    for i in range(last):
        if num_items(Items.Gold) > gold_before:
            break
        di = branches[i]
        g = spawn_drone(guided_searcher, di, di)
        if g:
            drones.append(g)
        else:
            guided_searcher(di, di)
    if num_items(Items.Gold) == gold_before:
        guided_searcher(branches[last], branches[last])
    for d in drones:
        wait_for(d)

# ---------- producer: scarcest-first ----------
def produce(item):
    if item == Items.Gold:
        if num_items(Items.Weird_Substance) < maze_substance_need():
            pumpkin_batch()
        else:
            maze_run()
        return True
    if item == Items.Bone:
        bone_run()
        return True
    if item == Items.Weird_Substance or item == Items.Pumpkin:
        pumpkin_batch()
        return True
    if item == Items.Cactus:
        cactus_once()
        return True
    if item == Items.Hay or item == Items.Wood or item == Items.Carrot:
        basic_sweep(item)
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

# Everything worth buying: repeatable UPGRADES (compound forever) + remaining
# feature unlocks. get_cost() returns the NEXT level's cost for upgrades, or
# None when maxed/owned -- so this list keeps pumping upgrade levels indefinitely.
def all_targets():
    return [Unlocks.Speed, Unlocks.Megafarm, Unlocks.Expand, Unlocks.Watering,
            Unlocks.Fertilizer, Unlocks.Carrots, Unlocks.Trees, Unlocks.Grass,
            Unlocks.Cactus, Unlocks.Pumpkins, Unlocks.Sunflowers, Unlocks.Polyculture,
            Unlocks.Mazes, Unlocks.Dinosaurs, Unlocks.Simulation, Unlocks.Leaderboard]

# distance to affordable = largest single-item shortfall (0 if affordable)
def deficit(cost):
    d = 0
    for item in cost:
        short = cost[item] - num_items(item)
        if short > d:
            d = short
    return d

# can produce() actually make this item? (mirror of produce's handled items)
def can_produce(item):
    if item == Items.Gold:
        return True
    if item == Items.Bone:
        return num_unlocked(Unlocks.Dinosaurs) > 0
    if item == Items.Weird_Substance or item == Items.Pumpkin:
        return True
    if item == Items.Cactus:
        return afford_plant(Entities.Cactus)   # only if we can pay to plant it
    if item == Items.Hay or item == Items.Wood or item == Items.Carrot:
        return True
    return False

# is every still-missing item of this cost something we can farm? If not (e.g.
# it needs Bone), pursuing it would stack gold forever without ever affording it.
def fundable(cost):
    for item in cost:
        if num_items(item) < cost[item] and not can_produce(item):
            return False
    return True

def pumpkin_unit():
    size = get_world_size()
    if size < 6:
        return size * size * size
    return 6 * size * size

def cactus_unit():
    size = get_world_size()
    tiles = size * size
    return tiles * tiles

def gold_unit():
    size = get_world_size()
    return size * size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)

def power_unit():
    size = get_world_size()
    # Expected full-field max-petal bonus harvest is about 15*8*(tiles/9).
    return size * size * 13

def stock_unit(item):
    size = get_world_size()
    tiles = size * size
    if item == Items.Hay:
        return tiles / 3
    if item == Items.Wood:
        return tiles * 5 / 3
    if item == Items.Carrot:
        return tiles / 3
    if item == Items.Pumpkin:
        return pumpkin_unit()
    if item == Items.Cactus:
        return cactus_unit()
    if item == Items.Weird_Substance:
        return pumpkin_unit()
    if item == Items.Gold:
        return gold_unit()
    if item == Items.Bone:
        return BONE_APPLES * BONE_APPLES
    if item == Items.Power:
        return power_unit()
    return 1

def stock_score(item):
    return num_items(item) / stock_unit(item)

def stockpile_item():
    items = [Items.Hay, Items.Wood, Items.Carrot, Items.Pumpkin,
             Items.Cactus, Items.Weird_Substance, Items.Gold]
    if AUTO_BONE and num_unlocked(Unlocks.Dinosaurs) > 0:
        items.append(Items.Bone)
    best = None
    best_s = 0
    for item in items:
        if can_produce(item):
            s = stock_score(item)
            if best == None or s < best_s:
                best = item
                best_s = s
    if best == None:
        return Items.Gold
    return best

# Buy every affordable upgrade/unlock, then keep all producible resources growing
# by farming the lowest normalized stockpile. Power is kept as a large reserve
# first because it doubles every other productive action.
def run():
    while True:
        quick_print(get_tick_count(), "gold", num_items(Items.Gold), "bone", num_items(Items.Bone), "cact", num_items(Items.Cactus), "pump", num_items(Items.Pumpkin), "weird", num_items(Items.Weird_Substance), "power", num_items(Items.Power))
        # 0. keep power topped up -> the engine consumes it for a GLOBAL 2x speed
        #    on every other action. Do this first so everything below runs at 2x.
        if num_items(Items.Power) < POWER_FLOOR and afford_plant(Entities.Sunflower):
            power_gen()
            continue
        # 1. buy every currently affordable upgrade/unlock (compounding)
        for t in all_targets():
            c = get_cost(t)
            if c != None and affordable(c):
                unlock(t)
        # 2. Rotate stockpiles by normalized inventory so no resource falls behind.
        produce(stockpile_item())

run()
