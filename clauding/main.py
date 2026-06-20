# clauding playthrough - Stage 12: adaptive controller, leaner pumpkin loop
# ASCII-only comments (in-game editor breaks on non-ASCII).
#
# Resource-triggered: build carrots with a balanced farm, then spend spare
# carrots on a whole-farm mega-pumpkin. Each crop in its optimal layout.
#
# Pumpkin loop is now unified (no separate till pass, no wasted re-scans):
#  - one pass does harvest+till+plant together (setup),
#  - later passes skip already-grown pumpkins (can_harvest gate) so a grown
#    tile costs only 2 sensors + the move, no re-plant/re-water attempts.

CARROT_HIGH = 250   # carrots to bank before a pumpkin run (tune to farm size)
WOOD_MIN = 20

def water_if_dry():
    if num_items(Items.Water) > 0 and get_water() < 0.5:
        use_item(Items.Water)

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
    size = get_world_size()
    while True:
        ready = True
        for x in range(size):
            for y in range(size):
                if can_harvest() and get_entity_type() == Entities.Pumpkin:
                    pass                      # grown pumpkin: done, just move on
                else:
                    ready = False
                    if can_harvest():
                        harvest()             # clear grown grass / leftovers
                    if get_ground_type() == Grounds.Grassland:
                        till()
                    e = get_entity_type()
                    if e == None or e == Entities.Dead_Pumpkin:
                        if not plant(Entities.Pumpkin):
                            return            # out of carrots -> bail, rebuild
                    # no watering here: a full pass takes far longer than the 2s
                    # pumpkin grow time, so tiles are grown by the next visit
                    # anyway. The remaining passes are caused by the 20% death
                    # roll, which watering does NOT help.
                move(North)
            move(East)
        if ready:
            harvest()                         # collect the merged mega-pumpkin
            return

def run():
    while True:
        clear()
        while num_items(Items.Carrot) < CARROT_HIGH:
            balanced_sweep()
        clear()
        pumpkin_mega_once()

run()
