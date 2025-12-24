import set_ground_type

def hay() :
	set_ground_type.toGrassland()

def wood() :
	set_ground_type.toGrassland()
	if (get_pos_x() % 2 != 0) and (get_pos_y() % 2 != 0)  : 
		plant(Entities.Tree)
	elif (get_pos_x() % 2 == 0) and (get_pos_y() % 2 == 0)  : 
		plant(Entities.Tree)
	else : 
		plant(Entities.Bush)
	
def carrot() : 
	set_ground_type.toSoil()
	plant(Entities.Carrot)
	
def pumpkin() :
	set_ground_type.toSoil()
	plant(Entities.Pumpkin)

def sunflower(): 
	set_ground_type.toSoil()
	plant(Entities.Sunflower)

def cactus():
	set_ground_type.toSoil()
	plant(Entities.Cactus)
		
	