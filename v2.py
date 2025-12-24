def find_lowest_item():
	gold_count = num_items(Items.Gold) * 1.5
	items = [
		(num_items(Items.Hay), Items.Hay),
		(num_items(Items.Wood), Items.Wood),
		(num_items(Items.Carrot), Items.Carrot),
		(num_items(Items.Pumpkin), Items.Pumpkin),
		(num_items(Items.Cactus), Items.Cactus),
		(gold_count, Items.Gold)
	]
	return min(items)[1]

def get_all_counts():
	return {
		Items.Hay: num_items(Items.Hay),
		Items.Wood: num_items(Items.Wood),
		Items.Carrot: num_items(Items.Carrot),
		Items.Pumpkin: num_items(Items.Pumpkin),
		Items.Cactus: num_items(Items.Cactus),
		Items.Power: num_items(Items.Power)
	}

def need_power():
	return num_items(Items.Power) < 500
