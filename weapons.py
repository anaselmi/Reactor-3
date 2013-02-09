from globals import *
import graphics as gfx
import numbers
import bullets
import random
import items
import life as lfe

random.seed()

def get_feed(weapon):
	return weapon[weapon['feed']]

def get_fire_mode(weapon):
	"""Returns current fire mode for a weapon."""
	return weapon['firemodes'][weapon['firemode']]

def fire(life,target):
	#TODO: Don't breathe this!
	if 'player' in life:
		weapon = life['firing']
	else:
		weapon = lfe.get_inventory_item(life,lfe.get_held_items(life,matches=[{'type': 'gun'}])[0])
	
	_mode = get_fire_mode(weapon)
	if _mode == 'single':
		_bullets = 1
	elif _mode == '3burst':
		_bullets = 3
	
	_ooa = False
	for i in range(_bullets):
		_feed = get_feed(weapon)
		
		if not _feed or (_feed and not _feed['rounds']):
			if 'player' in life:
				gfx.message('*Click*')
			
			_ooa = True
			continue
		
		direction = numbers.direction_to(life['pos'],target)
		direction += random.randint(-2,3)
		
		#TODO: Clean this up...
		#bullets.create_bullet(life['pos'],direction,5,life)
		_bullet = _feed['rounds'].pop()
		_bullet['pos'] = life['pos'][:]
		_bullet['owner'] = life['id']
		del _bullet['parent']
		items.move(_bullet,direction,15)
	
	if _ooa:
		if 'player' in life:
			gfx.message('You are out of ammo.')
	
	_fx = numbers.clip(life['facing'][0]-target[0],-1,1)
	_fy = numbers.clip(life['facing'][1]-target[1],-1,1)
	
	for life in LIFE:
		if life['pos'][0] == target[0] and life['pos'][1] == target[1]:
			life['aim_at'] = life['pos']
			break
	
	life['facing'] = (_fx,_fy)
	life['firing'] = None
