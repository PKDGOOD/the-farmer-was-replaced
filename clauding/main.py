# clauding playthrough - Stage 7: balanced farm (carrot / wood / hay)
# NOTE: ASCII-only comments. The in-game code editor throws
# IndexOutOfRangeException on non-ASCII (e.g. Korean) text, which garbles
# the program. Keep all deployed game scripts ASCII-only.
#
# Tiles are split by (x+y)%3 so all three resources are produced at once,
# and wood tiles (k==1) are never orthogonally adjacent -> trees grow with
# no adjacency penalty on farm sizes divisible by 3 (e.g. 6x6).
#   k==0 carrot (soil, watered)   k==1 wood (tree, bush fallback)   k==2 hay
# Carrots are gated behind a wood reserve so they never drain wood to 0
# (trees cost wood; draining it blocks tree planting).

RESERVE = 20

def farm_tile():
    if can_harvest():
        harvest()
    k = (get_pos_x() + get_pos_y()) % 3
    if k == 1:
        # wood: prefer tree (5 wood each), fall back to free bush
        if get_entity_type() == None:
            if not plant(Entities.Tree):
                plant(Entities.Bush)
    elif k == 0:
        # carrot: only plant when we have spare wood
        if get_ground_type() == Grounds.Grassland:
            till()
        if get_entity_type() == None and num_items(Items.Wood) > RESERVE:
            plant(Entities.Carrot)
        if num_items(Items.Water) > 0 and get_water() < 0.5:
            use_item(Items.Water)
    else:
        # hay: keep as grassland, grass regrows by itself
        if get_ground_type() == Grounds.Soil:
            till()

def run():
    size = get_world_size()
    while True:
        for x in range(size):
            for y in range(size):
                farm_tile()
                move(North)
            move(East)

run()
