import harvest
import plant
import moves

def execute():
	size = get_world_size()

	# 드론별 심기 + 행 정렬
	def make_worker(start_x):
		def worker():
			# 심기
			for x in range(start_x, size, 8):
				for y in range(size):
					moves.to(x, y)
					harvest.do()
					plant.cactus()

			# 담당 행 정렬 (오른쪽으로 큰 값)
			for y in range(start_x, size, 8):
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
		return worker

	# 8개 드론 심기 + 행 정렬
	spawn_drone(make_worker(1))
	spawn_drone(make_worker(2))
	spawn_drone(make_worker(3))
	spawn_drone(make_worker(4))
	spawn_drone(make_worker(5))
	spawn_drone(make_worker(6))
	spawn_drone(make_worker(7))
	make_worker(0)()

	# 열 정렬 (위로 큰 값) - 8드론 병렬
	def make_col_sorter(start_x):
		def sorter():
			for x in range(start_x, size, 8):
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
		return sorter

	spawn_drone(make_col_sorter(1))
	spawn_drone(make_col_sorter(2))
	spawn_drone(make_col_sorter(3))
	spawn_drone(make_col_sorter(4))
	spawn_drone(make_col_sorter(5))
	spawn_drone(make_col_sorter(6))
	spawn_drone(make_col_sorter(7))
	make_col_sorter(0)()

	moves.to(0, 0)
	harvest.do()
