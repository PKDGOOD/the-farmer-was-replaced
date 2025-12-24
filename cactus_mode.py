import harvest
import plant
import moves

def execute():
	size = get_world_size()

	def do_plant():
		harvest.do()
		plant.cactus()
	moves.snake_traverse(do_plant)

	# 행 정렬: 오른쪽으로 큰 값
	def sort_rows():
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
	def sort_cols():
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

	sort_rows()
	sort_cols()

	moves.to(0, 0)
	harvest.do()
