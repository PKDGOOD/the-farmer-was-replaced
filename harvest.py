import plant

def do() :
	if can_harvest():
		harvest()
		
	if num_items(Items.Water) > 0 and get_ground_type() == Grounds.Soil :
		use_item(Items.Water)
