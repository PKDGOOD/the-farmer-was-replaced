def do():
	if can_harvest():
		harvest()
	if get_ground_type() == Grounds.Soil:
		if get_water() < 0.75 and num_items(Items.Water) > 0:
			use_item(Items.Water)

def do_fast():
	if num_items(Items.Fertilizer) > 0:
		use_item(Items.Fertilizer)
	if can_harvest():
		if num_items(Items.Weird_Substance) > 0:
			use_item(Items.Weird_Substance)
		harvest()
	if get_ground_type() == Grounds.Soil:
		if get_water() < 0.75 and num_items(Items.Water) > 0:
			use_item(Items.Water)
