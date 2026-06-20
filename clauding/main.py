# clauding 플레이스루 — Stage 2: Wood 파밍 (덤불 심고 수확)
# ------------------------------------------------------------
# 가용 언락: while, if/else, can_harvest, move(E/N/S/W), plant(Bush), clear, speed
# 아직 없음: variables, operators, senses(get_pos/get_world_size), functions, for, till
#
# 다음 언락(Carrots/Trees 등)이 Wood를 요구 → 덤불(무료)을 심어 Wood 확보.
# 매 타일: 수확 가능하면 수확(다 자란 덤불=Wood, 잔디=Hay), 이어서 덤불 심기(빈칸 채움;
#          이미 덤불 있으면 plant 실패=1틱). move(East)로 한 행을 계속 순회.
#
# Senses 확보 시 → 2D 전체 순회 + Tree(체커보드, 그루당 Wood 5)로 교체 예정.
# Wood가 다음 언락 비용만큼 모이면 정지 후 다음 언락 진행.
while True:
    if can_harvest():
        harvest()
    plant(Entities.Bush)
    move(East)
