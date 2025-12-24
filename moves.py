def to(args):
	to(args[0], args[1])

def to(x, y):
	size = get_world_size()
	
	target_x = x
	if(x >= size):
		target_x = x- size
	
	target_y = y
	if(y >= size):
		target_y = y -size
	
	if target_x - get_pos_x() > 0 :
		while target_x != get_pos_x() :
			move(East)
	else :
		while target_x != get_pos_x() :
			move(West)
			
	if target_y - get_pos_y() > 0 :
		while target_y != get_pos_y() :
			move(North)
	else :
		while target_y != get_pos_y() :
			move(South)
			
def init():
	to(0,0)
			
	