import harvest
import plant
import moves

def execute():
	size = get_world_size()

	# 드론별 작업 함수 (심기 + 15꽃잎만 수확)
	def make_worker(start_x):
		def worker():
			for x in range(start_x, size, 8):
				for y in range(size):
					moves.to(x, y)
					harvest.do()
					plant.sunflower()

			# 15꽃잎(최대)인 것만 수확
			for x in range(start_x, size, 8):
				for y in range(size):
					moves.to(x, y)
					if measure() == 15:
						harvest.do()
		return worker

	# 드론 7개 생성 (각각 다른 열 담당)
	spawn_drone(make_worker(1))
	spawn_drone(make_worker(2))
	spawn_drone(make_worker(3))
	spawn_drone(make_worker(4))
	spawn_drone(make_worker(5))
	spawn_drone(make_worker(6))
	spawn_drone(make_worker(7))

	# 메인 드론은 0번 열 담당
	make_worker(0)()
