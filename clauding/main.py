# clauding 플레이스루 — Stage 4: 2D 당근 농장 (관수 + Wood 자동 폴백)
# ------------------------------------------------------------
# 가용: Senses, For, Operators, Carrots(till), Watering(use_item/get_water), Debug
# 아직 없음: Variables(맨 대입 회피), Functions, Costs, Auto_Unlock, Trees, Megafarm
#
# 전략: 당근(다음 자원 티어)을 2D 전체에서 재배. 관수로 성장 가속(수위<0.5 & 물 보유 시).
#   당근은 soil 필요 → grassland면 till. 당근 심기는 wood+hay 소모 →
#   Wood 떨어져 plant(Carrot) 실패하면 덤불(soil에서도 자람)로 폴백해 Wood 자급(자기균형).
#
# 매 타일: 수확 → (grassland면 till) → 빈칸이면 당근(실패 시 덤불) → 관수 → move(North).
# 다음: Functions+Costs+Auto_Unlock 확보 시 자동 언락 엔진(farmlib+reset_main) 배포.
while True:
    for col in range(get_world_size()):
        for row in range(get_world_size()):
            if can_harvest():
                harvest()
            if get_ground_type() == Grounds.Grassland:
                till()
            if get_entity_type() == None:
                if not plant(Entities.Carrot):
                    plant(Entities.Bush)
            if num_items(Items.Water) > 0 and get_water() < 0.5:
                use_item(Items.Water)
            move(North)
        move(East)
