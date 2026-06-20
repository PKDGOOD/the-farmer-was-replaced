# clauding playthrough - Stage 8: robust balanced farm (carrot / wood / hay)
# Fixes:
#  - Do NOT gate planting on get_entity_type()==None. Tilled/occupied tiles
#    can make that check skip planting. Just call plant(); it no-ops (1 tick)
#    if the tile is occupied or the ground is wrong.
#  - clear() once at start to reset the messy multi-stage field to clean
#    grass (inventory is kept; only field entities are removed).
# ASCII-only comments: the in-game editor throws on non-ASCII text.
#
# Tiles split by (x+y)%3: k==0 carrot (soil, watered), k==1 wood (tree>bush),
# k==2 hay (grass). Wood tiles are never orthogonally adjacent on sizes
# divisible by 3 (e.g. 6x6) -> trees grow with no adjacency penalty.
# Carrots gated behind a wood reserve so they never drain wood to 0
# (trees cost wood; draining it would block tree planting).

RESERVE = 20

def farm_tile():
    if can_harvest():
        harvest()
    k = (get_pos_x() + get_pos_y()) % 3
    if k == 1:
        # wood: try tree (5 each); if it can't (no wood / occupied) plant bush
        if not plant(Entities.Tree):
            plant(Entities.Bush)
    elif k == 0:
        # carrot: needs soil; only plant when wood is spare
        if get_ground_type() == Grounds.Grassland:
            till()
        if num_items(Items.Wood) > RESERVE:
            plant(Entities.Carrot)
        if num_items(Items.Water) > 0 and get_water() < 0.5:
            use_item(Items.Water)
    else:
        # hay: keep grassland so grass regrows on its own
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
