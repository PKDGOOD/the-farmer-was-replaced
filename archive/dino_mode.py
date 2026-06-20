import harvest
import plant

def execute():
	size = get_world_size()

	# 미로 체크 및 제거
	if not can_move(North) or not can_move(East) or not can_move(South) or not can_move(West):
		harvest()  # 미로 제거

	# 선인장 심기 (사과 생성 조건)
	for y in range(size):
		for x in range(size):
			harvest.do()
			plant.cactus()
			if x < size - 1:
				move(East)
		# 다음 행으로
		if y < size - 1:
			move(North)
			# 왼쪽 끝으로
			while get_pos_x() > 0:
				move(West)

	# 공룡 모자 착용
	change_hat(Hats.Dinosaur_Hat)

	target_length = 100
	current_length = 0
	max_moves = 10000
	total_moves = 0

	while current_length < target_length:
		apple_pos = measure()
		if apple_pos == None:
			change_hat(Hats.Gray_Hat)
			return
		target_x = apple_pos[0]
		target_y = apple_pos[1]

		# 사과까지 이동
		stuck_count = 0
		while get_pos_x() != target_x or get_pos_y() != target_y:
			total_moves = total_moves + 1
			if total_moves > max_moves:
				change_hat(Hats.Gray_Hat)
				return

			# 사과 방향으로 이동 시도
			moved = False
			dx = target_x - get_pos_x()
			dy = target_y - get_pos_y()

			# X축 우선
			if dx > 0:
				moved = move(East)
			elif dx < 0:
				moved = move(West)

			# X축 실패시 Y축
			if not moved:
				if dy > 0:
					moved = move(North)
				elif dy < 0:
					moved = move(South)

			# 둘 다 실패시 우회
			if not moved:
				moved = move(North) or move(East) or move(South) or move(West)

			# 완전히 막힘
			if not moved:
				stuck_count = stuck_count + 1
				if stuck_count > 3:
					change_hat(Hats.Gray_Hat)
					return
			else:
				stuck_count = 0

		current_length = current_length + 1

	change_hat(Hats.Gray_Hat)
