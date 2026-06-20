# clauding 플레이스루 — Stage 5: 함수형 균형 농장 (Carrot/Wood/Hay 동시 생산)
# ------------------------------------------------------------
# 신규 가용: Variables(맨 대입 OK), Functions(def/return/global).
# 문제: 당근은 wood+hay를 소모 → 단일작물 농장은 다른 자원이 0이 됨(직전 Stage4가 그랬음).
# 해결: 절대좌표 (x+y)%3 으로 타일을 3분할해 세 자원을 동시·지속 생산(자기균형).
#   k==0 당근(soil, 관수)  k==1 덤불(Wood)  k==2 잔디(Hay, 빈 grassland 자동성장)
# 아직 없음: Costs, Auto_Unlock, Lists/Dicts → 이게 들어오면 자동 언락 엔진으로 전환.

def farm_tile():
    if can_harvest():
        harvest()
    k = (get_pos_x() + get_pos_y()) % 3
    if k == 0:
        # 당근: soil 필요 + 관수로 성장 가속
        if get_ground_type() == Grounds.Grassland:
            till()
        if get_entity_type() == None:
            plant(Entities.Carrot)
        if num_items(Items.Water) > 0 and get_water() < 0.5:
            use_item(Items.Water)
    elif k == 1:
        # Wood: 나무(그루당 Wood 5). (x+y)%3==1 타일은 직교 인접이 없어 성장 페널티 0.
        #       나무 심기 실패(자원 부족 등) 시 무료 덤불로 폴백.
        if get_entity_type() == None:
            if not plant(Entities.Tree):
                plant(Entities.Bush)
    else:
        # Hay: grassland으로 되돌리고 비워두면 잔디 자동 성장
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
