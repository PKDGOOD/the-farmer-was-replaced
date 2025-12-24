import harvest
import plant
import moves

def plant_all():
	def do_plant():
		harvest.do()
		plant.cactus()
	moves.snake_traverse(do_plant)

def wait_all_grown():
	size = get_world_size()
	while True:
		all_ready = True
		for x in range(size):
			for y in range(size):
				moves.to(x, y)
				if not can_harvest():
					all_ready = False
		if all_ready:
			break

def sort_all():
	size = get_world_size()
	changed = True
	while changed:
		changed = False
		for x in range(size):
			for y in range(size):
				moves.to(x, y)
				current = measure()
				if x < size - 1:
					east = measure(East)
					if east < current:
						swap(East)
						changed = True
				if y < size - 1:
					north = measure(North)
					if north < current:
						swap(North)
						changed = True

def execute():
	plant_all()
	wait_all_grown()
	sort_all()
	moves.to(0, 0)
	harvest.do()
