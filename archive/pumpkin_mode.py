import harvest
import plant
import moves

def execute():
	size = get_world_size()

	# 드론별 심기 + 성장 대기
	def make_worker(start_x):
		def worker():
			# 심기
			for x in range(start_x, size, 8):
				for y in range(size):
					moves.to(x, y)
					harvest.do()
					plant.pumpkin()

			# 성장 대기 + 죽은 호박 처리
			done = False
			while not done:
				done = True
				for x in range(start_x, size, 8):
					for y in range(size):
						moves.to(x, y)
						entity = get_entity_type()
						if entity == Entities.Dead_Pumpkin:
							plant.pumpkin()
							done = False
						elif entity == Entities.Pumpkin:
							if not can_harvest():
								if num_items(Items.Fertilizer) > 0:
									use_item(Items.Fertilizer)
									if get_entity_type() == Entities.Dead_Pumpkin:
										plant.pumpkin()
								done = False

			# 수확
			for x in range(start_x, size, 8):
				for y in range(size):
					moves.to(x, y)
					harvest.do()
		return worker

	# 7개 드론 생성
	spawn_drone(make_worker(1))
	spawn_drone(make_worker(2))
	spawn_drone(make_worker(3))
	spawn_drone(make_worker(4))
	spawn_drone(make_worker(5))
	spawn_drone(make_worker(6))
	spawn_drone(make_worker(7))

	# 메인 드론
	make_worker(0)()
