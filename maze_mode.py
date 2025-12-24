import moves

def execute():
	size = get_world_size()

	# 기존 작물 정리 후 덤불 심기
	moves.to(0, 0)
	if can_harvest():
		harvest()
	plant(Entities.Bush)
	while not can_harvest():
		pass

	# 미로 생성
	substance = size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
	use_item(Items.Weird_Substance, substance)

	# 방향 설정 (오른손 법칙용)
	directions = [North, East, South, West]
	dir_idx = 0

	# 보물 찾을 때까지 반복
	while get_entity_type() != Entities.Treasure:
		# 오른쪽으로 돌기 시도
		right_idx = (dir_idx + 1) % 4
		if can_move(directions[right_idx]):
			dir_idx = right_idx
			move(directions[dir_idx])
		elif can_move(directions[dir_idx]):
			# 직진
			move(directions[dir_idx])
		else:
			# 왼쪽으로 돌기
			dir_idx = (dir_idx - 1) % 4

	# 보물 수확
	harvest()
