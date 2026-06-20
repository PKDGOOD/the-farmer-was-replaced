def to(x, y):
	size = get_world_size()
	target_x = x % size
	target_y = y % size

	while get_pos_x() != target_x:
		if (target_x - get_pos_x()) % size <= size // 2:
			move(East)
		else:
			move(West)

	while get_pos_y() != target_y:
		if (target_y - get_pos_y()) % size <= size // 2:
			move(North)
		else:
			move(South)

def snake_traverse(callback):
	size = get_world_size()
	for x in range(size):
		if x % 2 == 0:
			for y in range(size):
				to(x, y)
				callback()
		else:
			for y in range(size - 1, -1, -1):
				to(x, y)
				callback()

def init():
	to(0, 0)
