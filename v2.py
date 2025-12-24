def find_lowest_item() :
	hay = num_items(Items.Hay), Items.Hay
	wood = num_items(Items.Wood), Items.Wood
	carrot = num_items(Items.Carrot), Items.Carrot
	pumpkin = num_items(Items.Pumpkin), Items.Pumpkin
	cactus = num_items(Items.Cactus), Items.Cactus
	
	temp = hay
	if(wood[0] < temp[0]):
		temp = wood
	if(carrot[0] < temp[0]) :
		temp = carrot
	if(pumpkin[0] < temp[0]) : 
		temp = pumpkin
	if(cactus[0] < temp[0]) :
		temp = cactus
		
	return temp[1]