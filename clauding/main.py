# clauding playthrough - Stage 10: sustainable balanced farm + watering
# ASCII-only comments (in-game editor breaks on non-ASCII).
#
# The pumpkin farm stalled at carrot=0 (pumpkins cost carrots). This farm is
# self-sustaining: (x+y)%3 splits tiles into carrot / wood / hay so all base
# resources keep flowing, and slow crops (trees, carrots) are watered to grow
# faster. We already banked 500+ pumpkins; come back to pumpkins later (ideally
# once Megafarm gives parallel drones).
#
# Single-drone ceiling: the per-tile move() (200 ticks) dominates. Real speedups
# are Megafarm (parallel drones) and Sunflowers->Power (2x). Prioritize those.

RESERVE = 20

def water_if_dry():
    if num_items(Items.Water) > 0 and get_water() < 0.5:
        use_item(Items.Water)

def farm_tile():
    if can_harvest():
        harvest()
    k = (get_pos_x() + get_pos_y()) % 3
    if k == 1:
        # wood: tree (5 each) or free bush fallback; water (trees grow 7s)
        if not plant(Entities.Tree):
            plant(Entities.Bush)
        water_if_dry()
    elif k == 0:
        # carrot on soil, only when wood is spare; water (carrots grow 6s)
        if get_ground_type() == Grounds.Grassland:
            till()
        if num_items(Items.Wood) > RESERVE:
            plant(Entities.Carrot)
        water_if_dry()
    else:
        # hay: keep grassland so grass auto-grows (fast, no watering needed)
        if get_ground_type() == Grounds.Soil:
            till()

def run():
    clear()
    size = get_world_size()
    while True:
        for x in range(size):
            for y in range(size):
                farm_tile()
                move(North)
            move(East)

run()
