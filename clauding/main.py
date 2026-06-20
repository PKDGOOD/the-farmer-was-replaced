# clauding playthrough - Stage 13: AUTO-UNLOCK ENGINE
# ASCII-only comments (in-game editor breaks on non-ASCII).
#
# Costs (get_cost) and Auto_Unlock (unlock) are now available, so the bot drives
# its own progression: pick the next target unlock from a priority list, read
# its cost, farm whichever resource is the bottleneck, and unlock() when it can
# afford it. Targets it can't fund yet (e.g. needs gold before mazes work) are
# parked in 'blocked' and retried later.
#
# Farmable resources: hay / wood / carrot (balanced %3 farm) and pumpkin (mega).
# Gold/power/weird routines come in a later stage (after Mazes/Sunflowers wiring).

WOOD_MIN = 20
CARROT_HIGH = 250

def water_if_dry():
    if num_items(Items.Water) > 0 and get_water() < 0.5:
        use_item(Items.Water)

# --- balanced %3 farm: one pass making carrot / wood / hay ---
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

# --- one whole-farm mega-pumpkin cycle ---
def pumpkin_mega_once():
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
                    e = get_entity_type()
                    if e == None or e == Entities.Dead_Pumpkin:
                        if not plant(Entities.Pumpkin):
                            return
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

# returns True if it knows how to produce this item, else False
def farm_item(item):
    if item == Items.Pumpkin:
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

def target_list():
    return [
        Unlocks.Mazes,
        Unlocks.Polyculture,
        Unlocks.Cactus,
        Unlocks.Dinosaurs,
        Unlocks.Simulation,
        Unlocks.Megafarm,
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
            balanced_sweep()        # nothing actionable: keep resources flowing
            blocked = set()         # retry parked targets next round
            continue
        cost = get_cost(target)
        if affordable(cost):
            if not unlock(target):
                blocked.add(target)         # affordable but prereq missing
        else:
            item = worst_item(cost)
            if not farm_item(item):
                blocked.add(target)         # can't fund this item yet -> park

run()
