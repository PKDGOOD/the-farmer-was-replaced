# ============================================
# The Farmer Was Replaced - 게임 문서
# ============================================
#
# === 기본 API ===
#
# move(direction)      # North, East, South, West 방향으로 이동
# can_move(direction)  # 해당 방향으로 이동 가능한지 확인 (벽 체크)
# get_pos_x()          # 현재 X 좌표
# get_pos_y()          # 현재 Y 좌표
# get_world_size()     # 월드 크기
#
# plant(entity)        # 작물 심기
# harvest()            # 수확
# can_harvest()        # 수확 가능 여부
# get_entity_type()    # 현재 칸의 엔티티 타입 (1 tick 소요)
#
# use_item(item)       # 아이템 사용
# use_item(item, n)    # 아이템 n개 사용
# num_items(item)      # 아이템 보유 수량
#
# measure()            # 현재 칸 측정 (작물마다 다른 값 반환)
# measure(direction)   # 해당 방향 칸 측정
# swap(direction)      # 해당 방향과 작물 교환
#
# num_unlocked(unlock) # 해금 레벨 확인
#
#
# === 엔티티 (Entities) ===
#
# Entities.Grass       # 잔디
# Entities.Tree        # 나무
# Entities.Bush        # 덤불
# Entities.Carrot      # 당근
# Entities.Pumpkin     # 호박
# Entities.Dead_Pumpkin  # 죽은 호박
# Entities.Sunflower   # 해바라기
# Entities.Cactus      # 선인장
# Entities.Hedge       # 미로 벽
# Entities.Treasure    # 보물
#
#
# === 아이템 (Items) ===
#
# Items.Hay            # 건초
# Items.Wood           # 나무
# Items.Carrot         # 당근
# Items.Pumpkin        # 호박
# Items.Cactus         # 선인장
# Items.Gold           # 골드
# Items.Power          # 전력
# Items.Fertilizer     # 비료
# Items.Weird_Substance  # 이상한 물질 (미로 생성)
# Items.Egg            # 달걀
# Items.Bone           # 뼈
#
#
# === 작물별 정보 ===
#
# --- 덤불 (Bush) ---
# - 성장 조건: Grassland 또는 Soil
# - 성장 시간: 3.2 ~ 4.8초
# - 수확 확인: can_harvest() 사용
# - 비료: 2초씩 성장 시간 감소
#
# --- 호박 (Pumpkin) ---
# - 성장 조건: Soil
# - 감염: 비료 사용 시 감염 가능 → Entities.Dead_Pumpkin
# - 메가 호박: 큰 호박일수록 수확량 증가
#   - 기본 배율: max(1.0, 호박크기 - 1)
#   - 6x6 이상: (호박크기 - 1) * 2 배율
#   - 예: 1x1=1배, 2x2=1배, 3x3=2배, 6x6=10배, 10x10=18배
# - 호박 크기 확인: measure() 반환값
#
# --- 선인장 (Cactus) ---
# - 성장 조건: Soil
# - measure(): 선인장 크기 반환
# - 수확량: 가장 작은 N개 선인장만 수확 가능 (N = 월드 크기)
# - 전략: 오른쪽/위로 큰 값 정렬 → (0,0)에서 수확
#
# --- 해바라기 (Sunflower) ---
# - 성장 조건: Soil
# - measure(): 꽃잎 수 반환
# - 최대 꽃잎 수인 것만 수확해야 Power 획득 극대화
#
#
# === 미로 시스템 ===
#
# --- 생성 ---
# use_item(Items.Weird_Substance, amount)
# - amount = size * 2^(num_unlocked(Unlocks.Mazes) - 1)
# - 덤불이 있는 위치에서 미로 생성됨
#
# --- 탐색 ---
# measure()            # 보물 위치 (x, y) 튜플 반환
# can_move(direction)  # 벽 확인 (이동하지 않음)
# get_entity_type()    # Entities.Hedge (벽), Entities.Treasure (보물)
#
# --- 제거 ---
# harvest()            # 보물이 아닌 곳에서 수확하면 미로 전체 제거
#
#
# === 드론 시스템 ===
#
# spawn_drone(function)  # 현재 위치에 드론 생성, function 실행
# has_finished(function) # 해당 함수의 드론이 완료되었는지 확인
# wait_for(function)     # 해당 함수의 드론 완료까지 대기
#
# - 드론 수: num_unlocked(Unlocks.Drones)에 따라 증가
# - 드론 시작 위치: spawn_drone() 호출 시 현재 드론 위치
#
#
# === 비료 시스템 ===
#
# use_item(Items.Fertilizer)
# - 성장 시간 2초 감소
# - 호박: 감염 가능성 있음 → Dead_Pumpkin 체크 필요
# - 덤불/나무 등: 안전하게 사용 가능
#
#
# === 지형 (Ground) ===
#
# Grounds.Grassland    # 잔디밭
# Grounds.Soil         # 토양
# Grounds.Turf         # 잔디
#
# set_ground(ground)   # 지형 변경
# get_ground()         # 현재 지형 확인
#
#
# === 모자 시스템 ===
#
# change_hat(hat)  # 모자 변경 (200틱 소요)
# Hats.Gray_Hat    # 회색 모자
# Hats.Purple_Hat  # 보라색 모자
# Hats.Green_Hat   # 초록색 모자
# Hats.Brown_Hat   # 갈색 모자
# Hats.Dinosaur_Hat  # 공룡 모자 (스네이크 게임)
#
#
# === 공룡 모드 (뼈 수집) ===
#
# change_hat(Hats.Dinosaur_Hat)  # 공룡 모자 착용
# change_hat(Hats.Gray_Hat)      # 다른 모자로 변경 → 꼬리 수확
#
# --- 규칙 ---
# - 사과 먹으면 꼬리 길어짐 (스네이크 게임)
# - 꼬리 위로 이동 불가 (move() False 반환)
# - 농장 경계 못 넘음
# - 모자 벗으면: 꼬리길이² 만큼 뼈 획득
#   - 길이 10 → 100 뼈
#   - 길이 100 → 10000 뼈
#
# --- 사과 ---
# - 선인장 충분하면 자동 생성
# - measure() → 다음 사과 위치 (x, y) 튜플
#
# --- 속도 ---
# - 기본: 400틱 (일반 200틱의 2배)
# - 사과 1개당 3% 감소 (누적)
#
# --- 드론 ---
# - 공룡 모자는 1개뿐 → 단일 드론만 사용 가능
#
#
# === 팁 ===
#
# 1. get_entity_type()은 1 tick 소요 - 불필요한 호출 최소화
# 2. can_harvest()는 성장 완료 확인에 사용
# 3. 미로에서 moves.to() 사용 금지 - 무한 루프 위험
# 4. 미로 탐색: measure()로 보물 방향 확인 후 이동
# 5. 8드론: 4방향 x 2법칙(왼손/오른손) 미로 탐색
# 6. 해바라기: 15→7 꽃잎 순차 수확으로 8배 보너스 유지
