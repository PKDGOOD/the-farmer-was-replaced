import harvest
import plant
import moves

def plant_all():
	size = get_world_size()
	for x in range(size) :
		for y in range(size) :
			harvest.do()
			plant.cactus()
			moves.to(get_pos_x(), get_pos_y() + 1)
		moves.to(get_pos_x() + 1, get_pos_y())

def isSortedRow(y):	
	for x in range(get_world_size()):
		moves.to(x, y)
		if x != 0 and measure() < measure(West):
			return False
	return True
	
def sort_x(y):
	while not isSortedRow(y):
		for x in range(get_world_size()):
			moves.to(x, y)
			if x != 0 and measure() < measure(West):
				swap(West)
				
def isSortedRec(x):	
	for y in range(get_world_size()):
		moves.to(x, y)
		if y != 0 and measure() < measure(South):
			return False
	return True
	
def sort_y(x):
	while not isSortedRec(x):
		for y in range(get_world_size()):
			moves.to(x, y)
			if y != 0 and measure() < measure(South):
				swap(South)	

def sort():
	for i in range(get_world_size()):
		sort_x(i)
	for i in range(get_world_size()):
		sort_y(i)
	
	
def harvest_all():
	harvest.do()
		
def execute():
	plant_all()
	sort()
	harvest_all()
	
	
	
	