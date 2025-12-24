import harvest
import plant
import moves

def plant_all():
	size = get_world_size()
	for x in range(size) :
		for y in range(size) :
			harvest.do()
			plant.pumpkin()
			moves.to(get_pos_x(), get_pos_y() + 1)
		moves.to(get_pos_x() + 1, get_pos_y())

def isHarvestable():
	result = True
	size = get_world_size()
	for x in range(size) :
		for y in range(size) :
			if not can_harvest() :
				result = False
				plant.pumpkin()
			moves.to(get_pos_x(), get_pos_y() + 1)
		moves.to(get_pos_x() + 1, get_pos_y())
	
	if result != True:
		isHarvestable()
	
def harvest_all():
	harvest.do()
		
def execute():
	plant_all()
	
	isHarvestable()
		
		
	
	harvest_all()
	
	
	
	