# The Farmer Was Replaced — 전략 토대 문서

> **출처 우선순위**: ① 인게임 플레이어 문서 `EN/docs/unlocks/*.md` (메커니즘·수치) → ② `builtins.py` 도크스트링 (함수 시그니처·틱 비용) → ③ `EN/docs/scripting/*.md` (언어 의미).
> 실제 설치 경로: `~/Library/Application Support/Steam/steamapps/common/The Farmer Was Replaced/TheFarmerWasReplaced_Data/StreamingAssets/Languages/`
> 레포의 `__builtins__.py`(1307줄)·`game_notes.py`는 **구버전 사본**이며 오류가 있다. 이 문서가 그것을 대체한다. (정정표는 §9)

---

## 1. 틱 모델 — 게임의 본질 (`unlocks/timing.md`, 권위 원본)

게임의 모든 목표는 **"성공한 200틱 액션의 수를 최소화"** 하는 것이다. 기본 속도 **400틱/초**.

### 1-1. 코드 구문 비용
| 비용 | 구문 |
|---|---|
| **0틱 (무료)** | 함수 *호출*, 변수 읽기/쓰기, `import`, 모듈 `.` 접근, 단항 `-`/`not`, `return`/`break`/`continue` |
| **1틱** | 이항연산(`+ - * / // % ** and or` 및 비교), `if` 분기, 루프 *시작*(반복 자체는 무료), 함수 *정의*(`def`), 인덱싱(`a[i]`) |
| **1틱 (추가)** | 함수/모듈을 **인자·변수로 넘겨서** 호출하면 호출이 0→1틱. dict/set 인덱싱은 키 크기만큼 추가 |
| **1틱** | `pass` (정밀 딜레이 용도) |

→ 함수형/고차함수 패턴은 공짜가 아니다. **클로저를 드론에 넘기는 현재 패턴은 호출마다 1틱**을 더 낸다(루프 본문에선 무시 가능하나 인지할 것). `def`는 핫루프 밖으로 hoist.

### 1-2. 빌트인 액션 비용 (`builtins.py` 도크스트링)
| 비용 | 함수 |
|---|---|
| **0틱 (완전 무료)** | `get_time()`, `get_tick_count()`, `quick_print()` |
| **1틱** | 모든 센서: `can_harvest`, `can_move`, `get_pos_x/y`, `get_world_size`, `get_entity_type`, `get_ground_type`, `get_water`, `num_items`, `get_companion`, `measure`, `has_finished`, `max_drones`, `num_drones`, `get_cost`, `num_unlocked`, `random`, `abs`, `len`, `str` |
| **성공 200틱 / 실패 1틱** | `harvest`, `plant`, `move`, `swap`, `use_item`, `spawn_drone`, `unlock` |
| **항상 200틱** | `till`, `clear`, `change_hat`, `set_execution_speed`, `set_world_size`, `simulate`, `leaderboard_run` |
| **1초 (≈400 기본틱, 속도업 영향 안 받음)** | `print`, `do_a_flip`, `pet_the_piggy` |

### 1-3. 핵심 최적화 법칙
1. **`print()` 금지** — 1초(≈400틱)이고 속도업도 안 먹는다. 디버깅은 `quick_print()`(0틱) / `get_tick_count()`(0틱).
2. **1틱 센서로 200틱 액션을 게이트하라.** `can_harvest()`로 확인 후 `harvest()`. 실패 액션은 1틱이라 "시도 후 반환값 확인"도 유효.
3. **`harvest()`는 수확 불가 엔티티를 *파괴*하고도 200틱**을 쓴다 → 빈 칸/안 자란 칸을 센서로 걸러라.
4. **`use_item(item, n)`은 n과 무관하게 200틱** → 한 번에 몰아 쓰기.
5. **Power = 속도 화폐.** 보유 시 드론이 자동으로 2배 빠르게 액션(200틱이 실시간상 절반).

---

## 2. 테크트리 (Unlocks) — 전체 36개

`unlock(U)` = 200틱(성공)/1틱(실패). `get_cost(U, level)` = 비용 dict(1틱, `Costs` 해금 필요, 이미 해금 시 `None`). `num_unlocked(U)` = 업그레이드형이면 **1+업글횟수**, 아니면 0/1.

### 언어/프로그래밍
`Variables` `Operators` `Loops`(while) `Functions` `Lists` `Dictionaries`(dict+set) `Import` `Utilities`(min/max/abs)

### 센싱/도구
`Senses`(get_entity_type/get_ground_type/위치) · `Costs`(get_cost) · `Plant`(plant) · `Timing`(get_time/get_tick_count) · `Debug` · `Debug_2`(set_execution_speed/set_world_size) · `Simulation`(simulate) · `Leaderboard`(leaderboard_run) · `Auto_Unlock`

### 작물 (전부 업그레이드형 — "수확량과 비용 동시 증가")
`Grass`(건초) · `Carrots` · `Trees`(나무·덤불 수확량) · `Sunflowers`(+Power) · `Cactus` · `Pumpkins` · `Dinosaurs`(뼈) · `Mazes`(골드)

### 수확량 배수기 (작물 추가 없이 기존 산출 증폭 — **최고 레버리지**)
- **`Speed`** (업글형): 실행 속도 배수. `set_execution_speed(10)` = 9업글 상태.
- **`Megafarm`** (업글형): 다중 드론 + 드론 관리 함수. `max_drones()`로 현재 한도 조회.
- **`Watering`**: get_water/use_item(Water). 업글마다 물 획득 2배.
- **`Fertilizer`**: 성장시간 -2초. 업글마다 비료 획득 2배.
- **`Polyculture`**: get_companion() — **동반작물 수확 배수**.
- **`Expand`** (업글형): 농장 확장 + 이동(move) 해금. **업글 시 농장 초기화됨.**

> `Speed × Megafarm`이 모든 다중드론 리더보드의 지배적 곱셈 레버다.

---

## 3. 작물별 정확 공식 (`unlocks/*.md` 권위)

평균 성장시간(초) / 지형:
| 작물 | 성장 | 지형 | 산출 |
|---|---|---|---|
| Dinosaur(꼬리) | 0.2 | 잔디/토양 | (모드 §6) |
| **Grass** | 0.5 | 잔디 | Hay (자동 성장) |
| **Cactus** | 1 | 토양 | Cactus |
| **Pumpkin** | 2 | 토양 | Pumpkin |
| **Bush** | 4 | 잔디/토양 | Wood |
| **Sunflower** | 5 | 토양 | Power |
| **Carrot** | 6 | 토양 | Carrot |
| **Tree** | 7 | 잔디/토양 | Wood 5개 |

### Cactus — 정렬 후 연쇄 수확, 수확량 = (동시수확 수)²
- 크기 0~9 (`measure()`로 측정, `swap(dir)`로 교환).
- 다 자란 선인장을 수확할 때 **인접 선인장이 정렬 상태이면 재귀적으로 함께 수확**된다.
- 정렬 조건: 北·東 이웃이 **다 자랐고 ≥** 크기, 南·西 이웃이 **다 자랐고 ≤** 크기. (정렬되면 초록, 아니면 갈색)
- **수확량 = 동시 수확한 선인장 수의 제곱.** 8×8 전체가 단조 정렬돼 한 번에 수확되면 64² = **4096** Cactus.
- ⚠️ 목표는 **하나의 연속 단조 사슬**(보스트로페돈/뱀 순서). 행·열을 *독립적으로* 정렬하면 사슬이 끊긴다 (§9 코드결함).

### Pumpkin — 메가 병합, s×s 변 길이 s
- 다 자란 펌프킨들이 인접하면 메가 펌프킨으로 병합.
- **수확량: s≤5 → s³, s≥6 → 6·s²** (변 길이 s). 1×1=1, 2×2=8, 3×3=27, 4×4=64, 5×5=125, 6×6=216, **8×8=384**, 10×10=600.
- → **6×6 이상이면 풀 배율**. (스텁의 "count cubed"는 부정확; 위가 정답)
- 다 자랄 때 **20% 확률로 죽어** Dead_Pumpkin이 됨 (수확 불가, 새로 심으면 자동 제거). 죽음은 비료와 무관한 랜덤 이벤트.

### Sunflower — 최대 꽃잎 보너스 8x
- 꽃잎 7~15개. `measure()` = 꽃잎 수 (다 자라기 전에도 측정 가능).
- **농장에 ≥10개 있을 때 최대 꽃잎 개체를 수확하면 8배 Power.**
- 더 큰 꽃잎이 남아있는데 수확하면 **다음 수확도 보너스 상실.** 동률 최대는 아무거나 OK.
- Power는 액션 30회당 1 소비, 드론을 2배속으로 만든다.

### Tree — 인접 페널티
- 나무 1개당 Wood 5. **상하좌우 인접 나무 1개당 성장시간 2배** → 전부 심으면 16배 느림. **체커보드 배치 필수.**

### Bush / Grass
- Bush: Wood. Grass: 잔디에서 자동 성장 → Hay. (`Grass`/`Trees` 업글이 수확량 증가)

---

## 4. 배수기 시스템 상세

### Watering (`unlocks/watering.md`)
- 수위 0~1. **성장 속도 = 수위 0에서 1배 → 수위 1에서 5배 (선형).**
- 지반은 평균 **초당 현재 물의 1% 증발**(랜덤 변동). 고수위 유지는 비용 큼.
- 물 탱크 1개 = **0.25 물**, 10초마다 자동 +1탱크 (Watering 업글마다 2배).

### Fertilizer (`unlocks/fertilizer.md`)
- **남은 성장시간 -2초** (즉시). 10초마다 +1 (업글마다 2배).
- ⚠️ **감염**: 비료로 키운 작물은 감염 → 수확 시 산출 절반이 Weird_Substance가 됨.
- Weird_Substance를 작물에 쓰면 **자신+인접 작물의 감염 상태 토글**.
- → 비료는 **느린 작물(나무7·당근6·해바라기5)에만** 의미. 빠른 작물(선인장1·잔디0.5)엔 2초가 과해 200틱 낭비.

### Polyculture (`unlocks/polyculture.md`) — **현재 코드 100% 미사용, 거대 레버리지**
- 잔디·덤불·나무·당근은 올바른 동반작물을 두면 수확량 배수.
- `get_companion()` → `(원하는_타입, (x,y))`. 위치는 3칸 이내, 타입은 자신과 다른 것(Grass/Bush/Tree/Carrot 중) 랜덤.
- **배율: 기본 5배, 업그레이드마다 2배.** 산출 수확의 200틱은 동일하므로 **거의 공짜 배수**.

### Drones / Megafarm (`unlocks/megafarm.md`)
- **"메인 드론" 없음** — 전부 동등, 끝나면 사라짐. `spawn_drone(task,*args)`는 호출한 드론 위치에 생성, 한도 초과 시 `None` 반환(1틱).
- 권장 패턴: `if not spawn_drone(task): task()` — **한도에 자동 적응**. 하드코딩 8개 금지.
- `max_drones()` 한도, `num_drones()` 현재 수, `wait_for(drone)` 완료 대기(완료까지 틱 청구), `has_finished(drone)` 비차단 폴(1틱).
- **메모리 비공유**: 각 드론 독립 globals, 인자는 복사 전달.
- ⚠️ **Race condition**: 여러 드론이 같은 칸·같은 틱에 작용 가능. 공식 안티패턴 예시가 **현재 `harvest.py`의 물 로직과 정확히 일치** — `if get_water()<0.5: use_item(Water)`를 여러 드론이 돌리면 물 폭발적 낭비.

---

## 5. 미로 (Mazes, `unlocks/mazes.md`)

- 덤불 위에서 `use_item(Items.Weird_Substance, n)` → **n×n 미로** (업글 없을 때). 각 Mazes 업글이 **보물 2배 + 필요 substance 2배**.
- 전체 필드 미로: `substance = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)`.
- **보물 골드 = 미로 면적** (5×5 → 25 골드). (스텁의 "side length"는 오류)
- `harvest()`를 보물에서 → 골드. **보물 아닌 곳에서 harvest() → 미로 통째로 사라짐.**
- 🔑 **`measure()`는 미로 어디서든 보물 (x,y)를 반환** (1틱) → 현재 코드의 8드론 벽타기 대신 **직접 호밍**이 훨씬 적은 이동.
- `get_entity_type()`: 보물=`Entities.Treasure`, 그 외=`Entities.Hedge`. `can_move(dir)`로 벽 확인. 루프 없음(재사용 안 하면).
- 재사용(보물에 substance 또 쓰기, 최대 300회)은 **추가 골드 없음 + 루프 생성** → 스킵 권장.

---

## 6. 공룡 모드 (Dinosaurs, `unlocks/dinosaurs.md` — 권위 원본)

> 레포 `dino_mode.py`는 "고장"으로 커밋됨. 아래가 정확한 메커니즘. (스텁엔 공룡 문서가 없어 1차 분석이 일부 틀렸음 — 이 절이 정답)

- `change_hat(Hats.Dinosaur_Hat)` + **선인장 충분** → 사과가 자동 구매되어 드론 아래 배치.
- 사과 위에서 **이동하면 먹어서 꼬리 +1**, 그리고 새 사과가 랜덤 위치에 구매됨(여유 있을 때, 작물 없는 칸에만).
- 🔑 **사과 위에서 `measure()` → 다음 사과 위치 (x,y) 튜플.** (즉 사과 위에 있을 때만 좌표 반환)
- 꼬리가 뒤를 채움. **꼬리 위로 이동하면 `move()` False** (단, 마지막 꼬리 칸은 비켜나므로 그 칸엔 이동 가능). 농장 다 채우면 이동 불가 = 꼬리 최대.
- 공룡 모자 착용 중 **농장 경계 못 넘음**.
- 다른 모자로 바꾸면 **꼬리 수확 → 뼈 = 꼬리길이²** (길이 100 → 10000 뼈).
- ⚠️ **`move()`가 400틱**(일반 200의 2배). **사과 1개당 move 틱 -3%(내림)**: `ticks -= ticks*0.03//1`.
- **공룡 모자는 1개** → 한 드론만 착용. (Dinosaur 리더보드는 "다중 드론"이지만, 나머지 드론은 선인장 공급 등 보조 역할)

### 현재 `dino_mode.py` 버그
- `current_length`를 사과를 **실제로 먹었는지 검증 없이** while 반복마다 +1 → 꼬리 실제 길이와 어긋남.
- `measure()`를 사과가 아닌 칸에서 호출하면 좌표가 안 나옴 → 호밍 로직이 깨질 수 있음.

---

## 7. 리더보드 (목표 = 우리가 최적화하는 대상, `unlocks/leaderboard.md`)

- `leaderboard_run(leaderboard, filename, speedup)`. 성공 = 시뮬레이션 종료 시 성공조건 True. **목표 달성해도 프로그램이 끝나야 기록됨.** 변동 줄이려 **최소 2시간 평균** 업로드.
- **`Fastest_Reset`** (가장 권위): 단일 플롯에서 시작해 `Leaderboard` 재해금까지 **게임 전체 자동화**. → unlock 자동화 필요.

| 다중 드론 | 목표 | 싱글 드론(8×8) | 목표 |
|---|---|---|---|
| Hay | 2,000,000,000 | Hay_Single | 100,000,000 |
| Wood | 10,000,000,000 | Wood_Single | 500,000,000 |
| Carrots | 2,000,000,000 | Carrots_Single | 100,000,000 |
| Cactus | 33,554,432 | Cactus_Single | 131,072 |
| Pumpkins | 200,000,000 | Pumpkins_Single | 10,000,000 |
| Sunflowers(Power) | 100,000 | Sunflowers_Single | 10,000 |
| Maze(Gold) | 9,863,168 | Maze_Single | 616,448 |
| Dinosaur(Bone) | 33,488,928 | — | — |

### Simulation (`unlocks/simulation.md`) — **오프라인 튜닝 하네스, 현재 미사용**
- `simulate(filename, sim_unlocks, sim_items, sim_globals, seed, speedup)` → 걸린 시간(초) 반환. **실제 농장 상태 불변.**
- `seed` 고정 시 결정적 재현. `sim_unlocks=Unlocks`면 전부 최대 해금. → 드론 수·배치·수확 순서를 **재현 가능하게 A/B 테스트**하는 정석 도구.

---

## 8. 언어 함정 체크리스트 (`scripting/*.md`)

1. **정수형 없음 — 전부 float.** `5/2 == 2.5`. 인덱스/카운터엔 `//` 사용.
2. 비교 `< <= > >=`는 **숫자에만**. `== !=`는 모든 타입.
3. 복합대입은 `+= -= *= /= %=`만 (`//=`/`**=` 없음).
4. **리스트는 대입 시 별칭**(`b=a` → 공유). `.copy()` 없음 → 새로 빌드해야 복사.
5. **튜플만 dict 키로 보장** → 좌표 키는 `(x,y)`.
6. **`def`는 런타임 대입** → 호출 전에 실행돼야 하고, 루프 안 `def`는 매번 재생성(비용). 핫루프 밖으로 hoist.
7. 함수 내에서 global **쓰기**는 `global` 선언 필요. 루프/분기는 스코프 안 만듦(루프변수 누출).
8. **`import`는 파일을 실행**(부작용=틱 소비) 후 캐시(1회만). 라이브러리는 정의만 두거나 `if __name__=="__main__"` 가드.
9. **`while True:`는 정상** (반복 간 딜레이 있어 안 멈춤).
10. dict/set 반복 순서 **미보장**. **멤버십 `in`은 list보다 set/dict가 훨씬 빠름** (유일하게 문서화된 알고리즘 속도 규칙).

---

## 9. `game_notes.py` 정정표 (기존 노트의 오류)

| 기존 노트 주장 | 실제 (권위 원본) |
|---|---|
| `Items.Egg` 존재 | **없음**. 공룡 먹이는 `Entities.Apple`. |
| `Grounds.Turf`, `set_ground()/get_ground()` | **없음**. 지형은 `Grassland`/`Soil`뿐, `till()` 토글 + `get_ground_type()` 읽기. |
| 드론 수 = `num_unlocked(Unlocks.Drones)` | `Unlocks.Drones` **없음**. `Megafarm` 해금 + **`max_drones()`** 로 조회. |
| 펌프킨 배율 `max(1, 크기-1)`, 6×6=10배 | **s≤5: s³, s≥6: 6s²**. 6×6=216, 8×8=384. (선형 모델 완전 오류) |
| 선인장 "가장 작은 N개만 수확(N=월드크기)" | 그런 캡 없음. **정렬된 인접 연쇄를 재귀 수확, 산출 = 수확수²**. |
| 해바라기 보너스 "8배, 15→7 순차 수확" | 보너스 8배는 맞음. 단 **현재 최대 꽃잎**(필드 상대) 수확 + ≥10개 유지가 조건. "15→7 고정"은 근거 없음. |
| 비료가 펌프킨 감염 유발 | 죽음(20%)은 **성장 시 랜덤**, 비료 무관. 감염은 Weird_Substance 토글만. |
| 덤불 성장 3.2~4.8초 | 평균 **4초**만 권위. |
| 미로 골드 (불명확) | **면적** (5×5 → 25). |

---

## 10. 현재 코드 결함 + 전략 우선순위

### 코드 결함 (우선 수정)
1. **`dino_mode.py`** — 길이 카운트/측정 로직 버그 (§6). 실제 메커니즘대로 재작성 필요.
2. **`v2.py find_lowest_item`** — count 동률 시 `min()`이 Item 객체 비교로 떨어져 크래시 위험. Gold/Bone을 `num_unlocked(Mazes/Dinosaurs)` 게이트 없이 라우팅 → 준비 안 된 `maze_mode`(clear()로 농장 전체 삭제!)/깨진 `dino_mode` 진입.
3. **`cactus_mode.py`** — 행·열 독립 정렬은 단조 사슬을 못 만든다 → 수확이 조기 중단, 산출이 size²에 한참 못 미침. **뱀 순서 전체 정렬** 필요.
4. **`main.py` 외** — 드론 8개 하드코딩 + `range(start_x, size, 8)` 스트라이드. `max_drones()<8`이면 **일부 열이 통째로 누락**(미스폰 드론 담당). `max_drones()` 기반으로 전환.
5. **`harvest.py do_fast`** — 비료 무조건 사용(빠른 작물에 낭비) + 일반 수확 경로에서 Weird_Substance로 **의도치 않은 감염 토글**. 물 로직은 race condition.
6. **`sunflower_mode.py`** — 15→7 고정 스윕은 비최대 개체를 기본값으로 수확하고 ≥10 게이트를 깰 수 있음. 필드 최대 측정 후 선택 수확해야.
7. **`pumpkin_mode.py`** — 재심기 루프가 보드를 영구 비연속으로 만들 수 있음. 전체를 연속 성장(비료로 마무리)→확인→수확 흐름이 나음.

### 전략 우선순위 (레버리지 순)
1. 🔴 **Unlock/비용 자동화** (`get_cost`+`num_items`+`num_unlocked`) → `Fastest_Reset` 토대. 현재 구매 로직 전무. 실패 unlock은 1틱이라 폴링 저렴.
2. 🔴 **드론 수·필드 분할을 `max_drones()`로 구동** — 커버리지 버그 해결 + Speed×Megafarm 자동 스케일.
3. 🔴 **Polyculture 구현** (`get_companion()`) — 거의 공짜 배수, 최대 목표(Carrots 2B)에서 최대 효과.
4. 🔴 **선인장 뱀 순서 단조 정렬** → 8×8 한 방에 4096.
5. 🟡 **미로 `measure()` 직접 호밍** — O(면적) 벽타기 → 최단경로급.
6. 🟡 **`simulate()` 도입** — 결정적 오프라인 튜닝으로 전략 A/B.
7. 🟡 **해바라기 필드 최대 꽃잎 선택 수확** (8x 유지).
8. 🟢 **비료/물을 느린 작물에 한정 + `use_item(item,n)` 배치.**

---

## 11. Fastest_Reset 초기 상태 & 부트스트랩 제약 (선택된 목표)

`first_program.md` + `simulation.md` 교차 확인:

- **시작 상태**: 프로그래밍 기능 전부(Variables/Operators/Loops/Functions/Lists/Dictionaries/Import, if/while/for/break/continue)는 **항상 해금**. 추가로 `harvest()`·`do_a_flip()`만 사용 가능. **1×1 잔디밭**에서 잔디가 자동 성장 → `harvest()` → Hay. **Senses·Plant·Expand(move)·Costs 등 농사 언락은 전무.**
- **성공 조건**: `num_unlocked(Unlocks.Leaderboard) > 0`. 달성해도 **프로그램이 종료돼야** 기록됨.
- ⚠️ **닭-달걀 ①**: `get_cost()`는 `Costs` 언락 필요 → 시작 시점엔 비용 조회 불가. **첫 언락은 Hay를 모으며 `unlock(X)`를 폴링(실패 1틱)** 해 블라인드로 따야 하고, `Costs` 확보 후부터 전부 get_cost 기반 계획.
- ⚠️ **검증 필요 ②**: `unlock()` 함수가 `Auto_Unlock` 언락에 게이트되는지 미확인. 게이트라면 `Auto_Unlock`이 **첫 타깃**이어야 함 (없으면 자동화 자체 불가). → `simulate(unlocks={}, ...)`로 게임에서 직접 확인 가능.
- **초기 파밍**: 1×1에선 이동 불가 → `harvest()` 반복으로 Hay만 생산(잔디 성장 0.5s≈200틱). `Expand` 확보 후 move + 더 큰 농장, `Senses` 확보 후 `can_harvest()` 게이팅 가능.
- **설계 원칙**: 정적 비용표가 게임 파일에 없으므로 **데이터 주도**(get_cost/num_items/num_unlocked) + `simulate()`(시드 고정, 결정적)로 언락 순서·파라미터 오프라인 튜닝.
