import harvest
import plant
import moves

def execute():
	size = get_world_size()

	# 드론별 심기
	def make_planter(start_x):
		def planter():
			for x in range(start_x, size, 8):
				for y in range(size):
					moves.to(x, y)
					harvest.do()
					plant.cactus()
		return planter

	# 7개 드론 심기
	spawn_drone(make_planter(1))
	spawn_drone(make_planter(2))
	spawn_drone(make_planter(3))
	spawn_drone(make_planter(4))
	spawn_drone(make_planter(5))
	spawn_drone(make_planter(6))
	spawn_drone(make_planter(7))
	make_planter(0)()

	# 정렬 (swap은 병렬화 어려움 - 순차)
	# 행 정렬: 오른쪽으로 큰 값
	for y in range(size):
		for _ in range(size - 1):
			swapped = False
			moves.to(0, y)
			for x in range(size - 1):
				if measure(East) < measure():
					swap(East)
					swapped = True
				move(East)
			if not swapped:
				break

	# 열 정렬: 위로 큰 값
	for x in range(size):
		for _ in range(size - 1):
			swapped = False
			moves.to(x, 0)
			for y in range(size - 1):
				if measure(North) < measure():
					swap(North)
					swapped = True
				move(North)
			if not swapped:
				break

	moves.to(0, 0)
	harvest.do()
