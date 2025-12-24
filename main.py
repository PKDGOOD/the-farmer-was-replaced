import plant
import harvest
import moves
import v2
import cactus_mode
import pumpkin_mode
import maze_mode
import sunflower_mode

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

def do_normal_cycle():
	target = v2.find_lowest_item()

	if target == Items.Gold:
		maze_mode.execute()
	elif target == Items.Cactus:
		cactus_mode.execute()
	elif target == Items.Pumpkin:
		pumpkin_mode.execute()
	else:
		# 건초, 나무, 당근 - 8개 드론 병렬
		size = get_world_size()

		def make_worker(start_x):
			def worker():
				for x in range(start_x, size, 8):
					for y in range(size):
						moves.to(x, y)
						harvest.do()
						plant_by_target(target)
			return worker

		spawn_drone(make_worker(1))
		spawn_drone(make_worker(2))
		spawn_drone(make_worker(3))
		spawn_drone(make_worker(4))
		spawn_drone(make_worker(5))
		spawn_drone(make_worker(6))
		spawn_drone(make_worker(7))
		make_worker(0)()

while True:
	if v2.need_power():
		sunflower_mode.execute()
	else:
		do_normal_cycle()
