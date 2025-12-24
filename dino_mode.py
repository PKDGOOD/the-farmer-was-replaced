def execute():
	change_hat(Hats.Dinosaur_Hat)

	target_length = 100
	current_length = 0

	while current_length < target_length:
		apple_pos = measure()
		target_x = apple_pos[0]
		target_y = apple_pos[1]

		# 사과까지 이동
		stuck_count = 0
		while get_pos_x() != target_x or get_pos_y() != target_y:
			old_x = get_pos_x()
			old_y = get_pos_y()

			# 사과 방향으로 이동 시도
			moved = False
			dx = target_x - old_x
			dy = target_y - old_y

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
