def toGrassland(): 
	if get_ground_type() == Grounds.Soil :
		till()

def toSoil():
	if get_ground_type() == Grounds.Grassland :
		till()