# clauding 플레이스루 — Stage 0: 1x1 잔디밭에서 Hay 파밍
# ------------------------------------------------------------
# 현재 언락: harvest / do_a_flip / pass 뿐 (Loops·Senses·Variables 없음)
# 선행 조건: 언락 메뉴에서 Loops 구입 (Hay 5개)  ← 지금 Hay가 정확히 5개
#
# Senses가 없어 can_harvest() 게이팅이 불가하므로 단순 반복 수확.
# 안 자란 잔디 harvest()는 실패(1틱), 다 자란 잔디는 성공(200틱)이라 루프가 자체 페이싱됨.
# Hay가 다음 언락 비용만큼 모이면 정지(stop) 후 다음 단계로 진행.
while True:
    harvest()
