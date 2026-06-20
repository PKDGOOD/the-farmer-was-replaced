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
					plant.sunflower()
		return planter

	# 8개 드론 심기
	spawn_drone(make_planter(1))
	spawn_drone(make_planter(2))
	spawn_drone(make_planter(3))
	spawn_drone(make_planter(4))
	spawn_drone(make_planter(5))
	spawn_drone(make_planter(6))
	spawn_drone(make_planter(7))
	make_planter(0)()

	# 수확 함수 (꽃잎 수 지정)
	def make_harvester(start_x, petals):
		def harvester():
			for x in range(start_x, size, 8):
				for y in range(size):
					moves.to(x, y)
					if measure() == petals:
						harvest.do()
		return harvester

	# 15부터 7까지 순차적으로 수확 (8배 보너스 유지)
	for p in range(15, 6, -1):
		spawn_drone(make_harvester(1, p))
		spawn_drone(make_harvester(2, p))
		spawn_drone(make_harvester(3, p))
		spawn_drone(make_harvester(4, p))
		spawn_drone(make_harvester(5, p))
		spawn_drone(make_harvester(6, p))
		spawn_drone(make_harvester(7, p))
		make_harvester(0, p)()
