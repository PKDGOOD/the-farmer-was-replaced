import harvest
import plant
import moves

def plant_all():
	def do_plant():
		harvest.do()
		plant.pumpkin()
	moves.snake_traverse(do_plant)

def wait_all_grown():
	while True:
		all_ready = True
		size = get_world_size()
		for x in range(size):
			for y in range(size):
				moves.to(x, y)
				entity = get_entity_type()
				if entity == Entities.Pumpkin and not can_harvest():
					all_ready = False
				elif entity == Entities.Dead_Pumpkin or entity == None:
					plant.pumpkin()
					all_ready = False
		if all_ready:
			break

def harvest_all():
	size = get_world_size()
	for x in range(size):
		for y in range(size):
			moves.to(x, y)
			if can_harvest():
				harvest.do()

def execute():
	plant_all()
	wait_all_grown()
	harvest_all()
