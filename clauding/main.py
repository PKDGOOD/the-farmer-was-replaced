# clauding 플레이스루 — Stage 3: 2D 전체 순회 Wood 파머 (덤불)
# ------------------------------------------------------------
# 신규 가용: Operators, Senses(get_world_size/get_entity_type/get_pos), For(range), Carrots(till), Debug
# expand_2로 농장이 N×N 정사각형 → for + get_world_size()로 전체 순회.
# 아직 없음: Variables(맨 대입 회피), Functions, Costs, Auto_Unlock.
#
# 전략: Wood가 낮음(15) + 당근 심기는 wood+hay 소모 → 우선 덤불로 Wood 비축.
# 매 타일: 수확 가능하면 수확(덤불=Wood, 잔디=Hay) → 덤불 심기(빈칸 채움) → move(North).
# 한 열을 다 돌면 move(East)로 다음 열. while True로 계속.
#
# 다음: Wood 충분해지면 2D 당근 농장으로 교체. Functions+Costs+Auto_Unlock 확보 시 자동화 엔진 배포.
while True:
    for col in range(get_world_size()):
        for row in range(get_world_size()):
            if can_harvest():
                harvest()
            plant(Entities.Bush)
            move(North)
        move(East)
