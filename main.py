import plant
import harvest
import moves
import v2
import cactus_mode
import pumpkin_mode

def plant_by_target(target):
	if target == Items.Hay:
		plant.hay()
	elif target == Items.Wood:
		plant.wood()
	elif target == Items.Carrot:
		plant.carrot()
	elif target == Items.Pumpkin:
		plant.pumpkin()
	elif target == Items.Cactus:
		plant.cactus()
	else:
		plant.sunflower()

def do_sunflower_cycle():
	size = get_world_size()

	def plant_sunflowers():
		harvest.do()
		plant.sunflower()
	moves.snake_traverse(plant_sunflowers)

	while True:
		all_ready = True
		for x in range(size):
			for y in range(size):
				moves.to(x, y)
				if get_entity_type() == Entities.Sunflower:
					if not can_harvest():
						all_ready = False
				else:
					plant.sunflower()
					all_ready = False
		if all_ready:
			break

	max_petals = 0
	for x in range(size):
		for y in range(size):
			moves.to(x, y)
			if get_entity_type() == Entities.Sunflower:
				p = measure()
				if p > max_petals:
					max_petals = p

	for x in range(size):
		for y in range(size):
			moves.to(x, y)
			if get_entity_type() == Entities.Sunflower:
				if measure() == max_petals:
					harvest.do()

def do_normal_cycle():
	target = v2.find_lowest_item()

	if target == Items.Cactus:
		cactus_mode.execute()
	elif target == Items.Pumpkin:
		pumpkin_mode.execute()
	else:
		def do_farm():
			harvest.do()
			plant_by_target(target)
		moves.snake_traverse(do_farm)

while True:
	if v2.need_power():
		do_sunflower_cycle()
	else:
		do_normal_cycle()
