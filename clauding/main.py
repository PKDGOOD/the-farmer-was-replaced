# clauding 플레이스루 — Stage 2: Wood 파밍 (덤불, 1x3 농장)
# ------------------------------------------------------------
# 최초 Expand = 1x3 (폭1 x 높이3). 폭이 1이라 move(East)는 같은 칸으로 래핑 → North로 순회.
# 가용 언락: while, if/else, can_harvest, move(N/S/E/W), plant(Bush), clear, speed
# 아직 없음: variables, operators, senses(get_pos/get_world_size), functions, for, till
#
# 매 타일: 수확 가능하면 수확(다 자란 덤불=Wood, 잔디=Hay), 이어서 덤불 심기, move(North).
# 농장이 2D로 더 확장되고 Senses 확보되면 → 전체 2D 순회 + Tree(체커보드, Wood 5)로 교체.
while True:
    if can_harvest():
        harvest()
    plant(Entities.Bush)
    move(North)
