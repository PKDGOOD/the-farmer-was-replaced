def do():
	if can_harvest():
		harvest()
	if get_ground_type() == Grounds.Soil:
		if get_water() < 0.75 and num_items(Items.Water) > 0:
			use_item(Items.Water)
		if num_items(Items.Fertilizer) > 10:
			use_item(Items.Fertilizer)
