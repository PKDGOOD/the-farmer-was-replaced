import plant
import harvest
import moves
import v2
import cactus_mode
import pumpkin_mode

while True:
	while v2.find_lowest_item() == Items.Cactus:
		cactus_mode.execute()
	while v2.find_lowest_item() == Items.Pumpkin:
		pumpkin_mode.execute()
	
	size = get_world_size()
	if num_items(Items.Power) < 1000 :
		sunflowerMode = True
	else: 
		sunflowerMode = False
	for x in range(size) :
		for y in range(size) :
			harvest.do()
			if sunflowerMode:
				plant.sunflower()
			else :
				target = v2.find_lowest_item()
				if(target == Items.Hay or target == Entities.Grass) :
					plant.hay()
				elif(target == Items.Wood or target == Entities.Bush or target == Entities.Tree) :
					plant.wood()
				elif(target == Items.Carrot or target == Entities.Carrot) :
					plant.carrot()
				elif(target == Entities.Sunflower):
					plant.sunflower()
				else :
					plant.sunflower()
				
			moves.to(get_pos_x(), get_pos_y() + 1)
		moves.to(get_pos_x() + 1, get_pos_y())
		
	# 최대 꽃잎 수 찾기
	max_petals = 0
	for x in range(size) :
		for y in range(size) :
			moves.to(x, y)
			if get_entity_type() == Entities.Sunflower:
				max_petals = max(max_petals, measure())

	for x in range(size) :
		for y in range(size) :
			moves.to(x, y)
			if get_entity_type() == Entities.Sunflower and measure() == max_petals:
				harvest.do()
			if get_entity_type() != Entities.Sunflower :
				harvest.do()
				target = v2.find_lowest_item()
				if(target == Items.Hay or target == Entities.Grass) :
					plant.hay()
				elif(target == Items.Wood or target == Entities.Bush or target == Entities.Tree) :
					plant.wood()
				elif(target == Items.Carrot or target == Entities.Carrot) :
					plant.carrot()
				elif(target == Entities.Sunflower):
					plant.sunflower()
				elif not sunflowerMode:
					plant.sunflower()
			moves.to(get_pos_x(), get_pos_y() + 1)
		moves.to(get_pos_x() + 1, get_pos_y())

while True: 
	size = get_world_size()
	for x in range(size) :
		for y in range(size) :
			harvest.do()
			target = v2.find_lowest_item()

			if num_items(Items.Power) < 30 :
				target = Entities.Sunflower
			
			if(target == Items.Hay or target == Entities.Grass) :
				plant.hay()
			elif(target == Items.Wood or target == Entities.Bush or target == Entities.Tree) :
				plant.wood()
			elif(target == Items.Carrot or target == Entities.Carrot) :
				plant.carrot()
			elif(target == Items.Pumpkin):
				plant.pumpkin()
			elif(target == Items.Cactus):
				plant.cactus()
			elif(target == Entities.Sunflower):
				plant.sunflower()
			else :
				print(target)
			moves.to(get_pos_x(), get_pos_y() + 1)
		
		moves.to(get_pos_x() + 1, get_pos_y())





queue = []

while True:
	companion = get_companion()
	if companion == None :
		harvest.do()
		moves.to(get_pos_x() + 1, get_pos_y() + 1) 
		plant.carrot()
		continue
		
		
	moves.to(companion[1][0], companion[1][1])
	harvest.do()
	
	if num_items(Items.Power) < 10 :
		queue.append(Entities.Sunflower)
	else :
		queue.append(companion[0])
	#ueue.append(v2.find_lowest_item())
			
				
	if(len(queue) == 0) :
		target = None
	else :
		target = queue.pop()
	if target == None :
		plant.sunflower()
	else :
		if(target == Items.Hay or target == Entities.Grass) :
			plant.hay()
		elif(target == Items.Wood or target == Entities.Bush or target == Entities.Tree) :
			plant.wood()
		elif(target == Items.Carrot or target == Entities.Carrot) :
			plant.carrot()
		elif(target == Items.Pumpkin):
			plant.pumpkin()
		elif(target == Items.Cactus):
			plant.cactus()
		elif(target == Entities.Sunflower):
			plant.sunflower()
		else :
			print(target)

	if num_items(Items.Fertilizer) > 0 :
		use_item(Items.Fertilizer)
	