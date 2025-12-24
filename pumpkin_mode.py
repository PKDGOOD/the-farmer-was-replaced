import harvest
import plant
import moves

def plant_all():
	def do_plant():
		harvest.do()
		plant.pumpkin()
	moves.snake_traverse(do_plant)

def grow_all():
	size = get_world_size()
	while True:
		all_ready = True
		for x in range(size):
			for y in range(size):
				moves.to(x, y)
				entity = get_entity_type()
				if entity == Entities.Pumpkin:
					if can_harvest():
						if num_items(Items.Weird_Substance) > 0:
							use_item(Items.Weird_Substance)
					else:
						if num_items(Items.Fertilizer) > 0:
							use_item(Items.Fertilizer)
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
	grow_all()
	harvest_all()
