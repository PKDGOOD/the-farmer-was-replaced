# clauding playthrough - Stage 15: min-tick engine v2 (rush Megafarm via gold)
# ASCII-only comments (in-game editor breaks on non-ASCII).
#
# Strategy from first principles: a single drone is capped by serial 200-tick
# moves. The only way past that is Megafarm (parallel drones). Megafarm needs
# GOLD, which comes from mazes (now unlocked). Mazes are fueled by
# Weird_Substance, which fertilized pumpkins produce. So the whole chain is:
#   fertilized pumpkin -> weird_substance -> maze -> gold -> Megafarm.
#
# Priority = scarcest-resource-first: for the current target unlock, read
# get_cost() and produce the item with the largest deficit (worst_item), each
# resource via its own routine. Don't over-produce; let the cost drive it.

WOOD_MIN = 20
CARROT_HIGH = 250

def water_if_dry():
    if num_items(Items.Water) > 0 and get_water() < 0.5:
        use_item(Items.Water)

# ---------- crop routines ----------
def balanced_sweep():
    size = get_world_size()
    for x in range(size):
        for y in range(size):
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
            move(North)
        move(East)

def pumpkin_mega_once():
    # fertilize each pumpkin in place: resolves the 20% death roll without extra
    # scan passes AND infects them -> half the yield is Weird_Substance (fuel).
    size = get_world_size()
    while True:
        ready = True
        for x in range(size):
            for y in range(size):
                if can_harvest() and get_entity_type() == Entities.Pumpkin:
                    pass
                else:
                    ready = False
                    if can_harvest():
                        harvest()
                    if get_ground_type() == Grounds.Grassland:
                        till()
                    tries = 0
                    while tries < 6:
                        e = get_entity_type()
                        if e == Entities.Pumpkin and can_harvest():
                            break
                        if e == None or e == Entities.Dead_Pumpkin:
                            if not plant(Entities.Pumpkin):
                                return
                        if num_items(Items.Fertilizer) <= 0:
                            break
                        use_item(Items.Fertilizer)
                        tries = tries + 1
                move(North)
            move(East)
        if ready:
            harvest()
            return

def pumpkin_batch():
    if num_items(Items.Carrot) < CARROT_HIGH:
        clear()
        tries = 0
        while num_items(Items.Carrot) < CARROT_HIGH and tries < 40:
            balanced_sweep()
            tries = tries + 1
    clear()
    pumpkin_mega_once()

# ---------- maze -> gold ----------
def maze_substance_need():
    return get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)

def make_maze():
    if num_items(Items.Weird_Substance) < maze_substance_need():
        return False
    clear()                              # drone -> (0,0), field emptied
    plant(Entities.Bush)
    while not can_harvest():             # grow the bush (fertilize to speed)
        if num_items(Items.Fertilizer) > 0:
            use_item(Items.Fertilizer)
    use_item(Items.Weird_Substance, maze_substance_need())   # bush -> maze
    return True

def solve_maze():
    # right-hand wall follow until standing on the treasure, then harvest.
    # Mazes are simply-connected (no loops) so this always reaches it.
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
    harvest()                            # on treasure -> gold = maze area

def maze_run():
    if make_maze():
        solve_maze()

# ---------- producer: scarcest-first ----------
def produce(item):
    if item == Items.Gold:
        if num_items(Items.Weird_Substance) < maze_substance_need():
            pumpkin_batch()              # build fuel first (fertilized pumpkins)
        else:
            maze_run()
        return True
    if item == Items.Weird_Substance or item == Items.Pumpkin:
        pumpkin_batch()
        return True
    if item == Items.Hay or item == Items.Wood or item == Items.Carrot:
        balanced_sweep()
        return True
    return False                         # unknown item -> caller parks target

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

def target_list():
    return [
        Unlocks.Megafarm,     # parallel drones -- the real efficiency unlock
        Unlocks.Simulation,
        Unlocks.Dinosaurs,
        Unlocks.Leaderboard,
    ]

def run():
    blocked = set()
    while True:
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
