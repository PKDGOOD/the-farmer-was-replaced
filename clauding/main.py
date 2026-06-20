# clauding playthrough - Stage 11: adaptive resource-triggered controller
# ASCII-only comments (in-game editor breaks on non-ASCII).
#
# Instead of a fixed per-tile crop split, this checks stock levels and runs the
# best routine for what is needed, each crop in its OWN optimal layout:
#   - carrots below CARROT_HIGH -> balanced farm builds carrots (+wood+hay)
#   - carrots at/above it       -> spend spare carrots on a whole-farm
#                                  mega-pumpkin (max yield = one big block)
# If carrots run out mid-pumpkin it bails and rebuilds; it never deadlocks.
# This is the manual precursor to the get_cost/Auto_Unlock auto-engine, which
# would trigger off real unlock costs instead of fixed thresholds.

CARROT_HIGH = 250   # carrots needed before a pumpkin run (tune to farm size)
WOOD_MIN = 20       # keep this much wood so carrots/trees can be planted

def water_if_dry():
    if num_items(Items.Water) > 0 and get_water() < 0.5:
        use_item(Items.Water)

# --- balanced sweep: one pass producing carrot / wood / hay ---
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

# --- one whole-farm mega-pumpkin cycle (spends carrots) ---
def pumpkin_mega_once():
    size = get_world_size()
    # ensure whole farm is soil
    for x in range(size):
        for y in range(size):
            if get_ground_type() == Grounds.Grassland:
                till()
            move(North)
        move(East)
    # plant + grow until every tile is a grown pumpkin (merged), then harvest
    while True:
        ready = True
        for x in range(size):
            for y in range(size):
                e = get_entity_type()
                if e == None or e == Entities.Dead_Pumpkin:
                    if not plant(Entities.Pumpkin):
                        return            # out of carrots -> bail, rebuild
                    ready = False
                elif not can_harvest():
                    ready = False
                    water_if_dry()        # speed growth (water never infects)
                move(North)
            move(East)
        if ready:
            harvest()                     # collect the merged mega-pumpkin
            return

def run():
    while True:
        clear()
        while num_items(Items.Carrot) < CARROT_HIGH:
            balanced_sweep()
        clear()
        pumpkin_mega_once()

run()
