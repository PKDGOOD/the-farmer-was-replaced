# clauding 플레이스루 — Stage 7: 균형 농장 (나무 Wood 고갈 버그 수정)
# ------------------------------------------------------------
# 버그: 당근(k=0)이 wood를 0까지 소모 → 나무는 wood가 있어야 심기는데 실패 → 덤불 폴백만 됨.
# 수정: 당근은 wood 여유(> RESERVE)일 때만 심어 wood를 마르지 않게 함.
#   부트스트랩(wood=0): 무료 덤불이 wood를 쌓음 → wood 차면 나무(그루당 5) 자동 전환.
# 좌표 (x+y)%3 분할: 6x6 등 3의 배수 농장에서 나무 직교 인접 0(성장 페널티 없음).
#   k==0 당근(soil,관수)  k==1 나무>덤불(Wood)  k==2 잔디(Hay)
# 아직 없음: Costs, Auto_Unlock → 확보 시 자동 언락 엔진으로 전환.

RESERVE = 20  # 당근에 쓰기 전 유지할 최소 wood (나무 굶김/wood 고갈 방지)

def farm_tile():
    if can_harvest():
        harvest()
    k = (get_pos_x() + get_pos_y()) % 3
    if k == 1:
        # Wood: 나무 우선, 실패(wood 부족)하면 무료 덤불 → wood 항상 자급
        if get_entity_type() == None:
            if not plant(Entities.Tree):
                plant(Entities.Bush)
    elif k == 0:
        # 당근: wood 여유 있을 때만 (wood 고갈 방지)
        if get_ground_type() == Grounds.Grassland:
            till()
        if get_entity_type() == None and num_items(Items.Wood) > RESERVE:
            plant(Entities.Carrot)
        if num_items(Items.Water) > 0 and get_water() < 0.5:
            use_item(Items.Water)
    else:
        # Hay: grassland으로 두면 잔디 자동 성장
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
