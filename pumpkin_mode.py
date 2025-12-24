import harvest
import plant
import moves

def execute():
	size = get_world_size()

	def do_plant():
		harvest.do()
		plant.pumpkin()
	moves.snake_traverse(do_plant)

	while True:
		all_ready = True
		for x in range(size):
			for y in range(size):
				moves.to(x, y)
				entity = get_entity_type()
				if entity == Entities.Dead_Pumpkin:
					plant.pumpkin()
					all_ready = False
				elif entity == Entities.Pumpkin:
					while True:
						if can_harvest():
							break
						if num_items(Items.Fertilizer) > 0:
							use_item(Items.Fertilizer)
							if get_entity_type() == Entities.Dead_Pumpkin:
								plant.pumpkin()
								break
		if all_ready:
			break

	harvest.do()
