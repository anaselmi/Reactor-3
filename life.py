from globals import *
import graphics as gfx
import pathfinding
import logging
import copy
import json
import os

def load_life(life):
	with open(os.path.join(LIFE_DIR,life+'.json'),'r') as e:
		return json.loads(e.readline())

def calculate_base_stats(life):
	stats = {'arms': None,
		'legs': None,
		'melee': None,
		'speed_max': LIFE_MAX_SPEED}
	race_type = None
	
	_flags = life['flags'].split('|')
	
	for flag in _flags:
		if _flags.index(flag) == 0:
			race_type = flag
		
		elif flag.count('LEGS'):
			stats['legs'] = flag.partition('[')[2].partition(']')[0].split(',')
		
		elif flag.count('ARMS'):
			stats['arms'] = flag.partition('[')[2].partition(']')[0].split(',')
		
		elif flag.count('MELEE'):
			stats['melee'] = flag.partition('[')[2].partition(']')[0].split(',')
	
	stats['speed_max'] = LIFE_MAX_SPEED-(len(stats['legs'])*10)
	
	return stats

def initiate_life(name):
	if name in LIFE_TYPES:
		logging.warning('Life type \'%s\' is already loaded. Reloading...' % name)
	
	_life = load_life(name)
	
	if not 'icon' in _life:
		logging.warning('No icon set for life type \'%s\'. Using default (%s).' % (name,DEFAULT_ICON))
		_life['tile'] = DEFAULT_ICON
	
	if not 'flags' in _life:
		logging.error('No flags set for life type \'%s\'. Errors may occur.' % name)
	
	_life.update(calculate_base_stats(_life))
	
	LIFE_TYPES[name] = _life
	
	return _life

def initiate_limbs(body):
	for limb in body:
		#If canhold or canstore
		body[limb]['storing'] = []
		body[limb]['holding'] = []
		initiate_limbs(body[limb]['attached'])

def create_life(type,position=(0,0),name=('Test','McChuckski'),map=None):
	if not type in LIFE_TYPES:
		raise Exception('Life type \'%s\' does not exist.' % type)
	
	#TODO: Any way to get rid of this call to `copy`?
	_life = copy.deepcopy(LIFE_TYPES[type])
	_life['name'] = name
	_life['speed'] = _life['speed_max']
	_life['pos'] = list(position)
	_life['map'] = map
	_life['path'] = []
	_life['actions'] = []
	_life['flags'] = {}
	
	initiate_limbs(_life['body'])
	LIFE.append(_life)
	
	return _life

def set_state(life,flag,state):
	life['flags'][flag] = state

def get_state(life,flag):
	if flag in life['flags']:
		return life['flags'][flag]
	
	raise Exception('State \'%s\' does not exist.' % flag)

def path_dest(life):
	if not life['path']:
		return None
	
	return tuple(life['path'][len(life['path'])-1])

def walk(life,to):
	if life['speed']:
		life['speed'] -= 1
		return False
	else:
		life['speed'] = life['speed_max']
	
	_dest = path_dest(life)
	
	if not _dest == tuple(to):
		_path = pathfinding.astar(start=life['pos'],end=to,size=MAP_SIZE,omap=life['map'])
		life['path'] = _path.find_path(life['pos'])
		print 'Setting path',life['path']
	
	return walk_path(life)

def walk_path(life):
	if life['path']:
		life['pos'] = list(life['path'].pop(0))
		print 'Walking',life['pos']
		
		if life['path']:
			return False
		else:
			print 'Empty path...'
			return True
	else:
		print 'here?'
		return False

def get_highest_action(life):
	_actions = {'action': None,'lowest': -1}
	
	for action in life['actions']:
		if action['score'] > _actions['lowest']:
			_actions['lowest'] = action['score']
			_actions['action'] = action
	
	if _actions['action']:
		return _actions['action']
	else:
		return None

def add_action(life,action,score):
	life['actions'].append({'action': action,'score': score})

def perform_action(life):
	_action = get_highest_action(life)
	
	if not _action in life['actions']:
		return False

	_score = _action['score']
	_action = _action['action']
	
	if _action['action'] == 'move':
		if walk(life,_action['to']):
			life['actions'].remove({'action':_action,'score':_score})

def tick(life):
	perform_action(life)

def show_life_info(life):
	for key in life:
		if key == 'body':
			continue
		
		print '%s: %s' % (key,life[key])
	
	return True

def draw_life():
	for life in LIFE:
		if life['pos'][0] >= CAMERA_POS[0] and life['pos'][0] <= CAMERA_POS[0]+MAP_WINDOW_SIZE[0] and\
			life['pos'][1] >= CAMERA_POS[1] and life['pos'][1] <= CAMERA_POS[1]+MAP_WINDOW_SIZE[1]:
			_x = life['pos'][0] - CAMERA_POS[0]
			_y = life['pos'][1] - CAMERA_POS[1]
			gfx.blit_char(_x,_y,life['icon'],white,None)

#Conductor
def tick_all_life():
	for life in LIFE:
		tick(life)
	
#initiate_life('Human')
#_life = create_life('Human',['derp','yerp'])
#_life = create_life('Human',['nope','yerp'])
#_life['speed'] = 50
#_life['speed_max'] = 50
#_life = create_life('Human',['zooom','yerp'])
#add_action(_life,{'action': 'move', 'to': (5,5)},200)
##add_action(_life,'eat',30)
#_life['speed'] = 1
#_life['speed_max'] = 1

#for a in range(500):
	#tick_all_life()
##show_life_info(_life)
