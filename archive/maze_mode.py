import moves
import set_ground_type

def execute():
	size = get_world_size()

	# 미로 안에 있는지 체크
	def is_in_maze():
		for d in [North, East, South, West]:
			if not can_move(d):
				return True
		return False

	# 이미 미로 안에 있으면 harvest()로 제거
	if is_in_maze():
		harvest()
		execute()
		return

	# 전체 필드 초기화
	clear()

	# 중앙에 덤불 심기
	center = size // 2
	moves.to(center, center)
	set_ground_type.toGrassland()
	plant(Entities.Bush)
	while not can_harvest():
		if num_items(Items.Fertilizer) > 0:
			use_item(Items.Fertilizer)

	# 현재 골드 수 기억
	gold_before = num_items(Items.Gold)

	# 방향 회전
	def get_right(d):
		if d == North:
			return East
		if d == East:
			return South
		if d == South:
			return West
		return North

	def get_left(d):
		if d == North:
			return West
		if d == West:
			return South
		if d == South:
			return East
		return North

	def get_back(d):
		if d == North:
			return South
		if d == South:
			return North
		if d == East:
			return West
		return East

	# 탐색 함수 (시작방향, 오른손/왼손 법칙)
	def make_searcher(start_dir, use_right_hand):
		def searcher():
			# 미로 생성될 때까지 대기
			while get_entity_type() != Entities.Hedge:
				pass

			facing = start_dir

			while get_entity_type() != Entities.Treasure:
				if num_items(Items.Gold) > gold_before:
					return

				right = get_right(facing)
				left = get_left(facing)
				back = get_back(facing)

				if use_right_hand:
					# 오른손 법칙: 오른쪽 -> 앞 -> 왼쪽 -> 뒤
					if can_move(right):
						move(right)
						facing = right
					elif can_move(facing):
						move(facing)
					elif can_move(left):
						move(left)
						facing = left
					elif can_move(back):
						move(back)
						facing = back
				else:
					# 왼손 법칙: 왼쪽 -> 앞 -> 오른쪽 -> 뒤
					if can_move(left):
						move(left)
						facing = left
					elif can_move(facing):
						move(facing)
					elif can_move(right):
						move(right)
						facing = right
					elif can_move(back):
						move(back)
						facing = back

			harvest()
		return searcher

	# 8개 드론: 4방향 x 2법칙
	spawn_drone(make_searcher(North, True))   # 북 오른손
	spawn_drone(make_searcher(North, False))  # 북 왼손
	spawn_drone(make_searcher(East, True))    # 동 오른손
	spawn_drone(make_searcher(East, False))   # 동 왼손
	spawn_drone(make_searcher(South, True))   # 남 오른손
	spawn_drone(make_searcher(South, False))  # 남 왼손
	spawn_drone(make_searcher(West, True))    # 서 오른손

	# 미로 생성
	substance = size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
	use_item(Items.Weird_Substance, substance)

	# 메인: 서 왼손
	make_searcher(West, False)()
