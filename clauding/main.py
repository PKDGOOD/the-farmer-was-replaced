# clauding playthrough - Stage 9: mega-pumpkin farm (single drone)
# ASCII-only comments (in-game editor breaks on non-ASCII).
#
# The whole farm is one pumpkin block. When every pumpkin is fully grown they
# merge into one giant pumpkin; harvesting it yields s^3 (s<=5) or 6*s^2 (s>=6)
# pumpkins, where s = farm side length. ~1 in 5 pumpkins dies at maturity
# (Dead_Pumpkin) and must be replanted until the whole block is alive+grown.
#
# Notes:
#  - Pumpkins cost CARROTS to plant. If carrots run out the block can't
#    complete; switch back to the balanced farm (git: Stage 8) to refill.
#  - No fertilizer on pumpkins: it infects them and halves the mega yield.

def all_to_soil():
    size = get_world_size()
    for x in range(size):
        for y in range(size):
            if get_ground_type() == Grounds.Grassland:
                till()
            move(North)
        move(East)

def run():
    clear()
    all_to_soil()
    size = get_world_size()
    while True:
        ready = True
        for x in range(size):
            for y in range(size):
                e = get_entity_type()
                if e == None or e == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)   # costs carrots; no-op if none
                    ready = False
                elif not can_harvest():
                    ready = False             # a pumpkin still growing
                move(North)
            move(East)
        if ready:
            harvest()                         # all grown -> merged mega -> collect

run()
