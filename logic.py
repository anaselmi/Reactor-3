from globals import *

import libtcodpy as tcod
import graphics as gfx
import alife as alfe

import encounters
import worldgen
import effects
import numbers
import weather
import timers
import dialog
import cache
import menus
import items
import life
import smp

import logging
import random
import time

def can_tick(check=True):
	if SETTINGS['controlling'] and not EVENTS:
		if SETTINGS['paused'] and not LIFE[SETTINGS['controlling']]['actions'] and not LIFE[SETTINGS['controlling']]['dead']:
			return False
	
	if not check:
		if process_events():
			return False
	elif EVENTS:
		return False
	
	if menus.get_menu_by_name('Select Limb')>-1 or menus.get_menu_by_name('Select Target')>-1:
		return False
	
	if SETTINGS['controlling']:
		if MENUS:
			return False
		
		if LIFE[SETTINGS['controlling']]['targeting']:
			return False
	
		if life.has_dialog(LIFE[SETTINGS['controlling']]):
			return False
	
	if not check:
		WORLD_INFO['tps'] += 1
		
		if WORLD_INFO['ticks']-WORLD_INFO['tps_time']>=30:
			WORLD_INFO['tps'] = 0
			WORLD_INFO['tps_time'] = WORLD_INFO['ticks']
	
	if WORLD_INFO['tps'] > TPS:
		return False
	
	return True

def tick_all_objects(source_map):
	if not can_tick(check=False):
		return False
	
	if SETTINGS['controlling']:
		_in_combat = False
		for alife in [LIFE[i] for i in LIFE]:
			if SETTINGS['controlling'] == alife['id']:
				continue
			
			if alife['asleep'] or alife['dead']:
				continue
			
			_x,_y = alife['pos'][:2]
			
			if alife['pos'][0]>CAMERA_POS[0]:
				_x = alife['pos'][0]-CAMERA_POS[0]
			
			if alife['pos'][1]>CAMERA_POS[1]:
				_y = alife['pos'][1]-CAMERA_POS[1]
			
			if _x>=40:
				continue
			
			if _y>=40:
				continue
			
			if not LOS_BUFFER[0][_y, _x]:
				continue
			
			_targets = alfe.judgement.get_combat_targets(LIFE[SETTINGS['controlling']])
			if _targets and SETTINGS['controlling'] in _targets:
				_in_combat = True
	
	effects.calculate_all_effects()
	tick_world()
	timers.tick()
	items.tick_all_items(source_map)
	
	#if SETTINGS['smp']:
	#	smp.scan_all_surroundings()
	
	life.tick_all_life(source_map)
	
	return True

def tick_world():
	WORLD_INFO['ticks'] += 1
	alfe.groups.get_group_relationships()
	
	if WORLD_INFO['real_time_of_day'] < WORLD_INFO['length_of_day']:
		WORLD_INFO['real_time_of_day'] += WORLD_INFO['time_scale']
	else:
		WORLD_INFO['real_time_of_day'] = 0
		WORLD_INFO['day'] += 1
		weather.change_weather()
	
	if WORLD_INFO['real_time_of_day']>=WORLD_INFO['length_of_day']-1500 or WORLD_INFO['real_time_of_day']<=1000:
		if WORLD_INFO['time_of_day'] == 'day':
			gfx.message('Night falls.')
		
		WORLD_INFO['time_of_day'] = 'night'
	else:
		if WORLD_INFO['time_of_day'] == 'night':
			gfx.message('The sun rises.')
		
		WORLD_INFO['time_of_day'] = 'day'
	
	if WORLD_INFO['life_spawn_interval'][0]>0:
		WORLD_INFO['life_spawn_interval'][0] -= 1
	elif not WORLD_INFO['life_spawn_interval'][0]:
		worldgen.generate_life()
			
		WORLD_INFO['life_spawn_interval'][0] = random.randint(WORLD_INFO['life_spawn_interval'][1][0], WORLD_INFO['life_spawn_interval'][1][1])
		
		logging.info('Reset life spawn clock: %s' % WORLD_INFO['life_spawn_interval'][0])
	
	if WORLD_INFO['wildlife_spawn_interval'][0]>0:
		WORLD_INFO['wildlife_spawn_interval'][0] -= 1
	elif not WORLD_INFO['wildlife_spawn_interval'][0]:
		worldgen.generate_wildlife()
			
		WORLD_INFO['wildlife_spawn_interval'][0] = random.randint(WORLD_INFO['wildlife_spawn_interval'][1][0], WORLD_INFO['wildlife_spawn_interval'][1][1])
		
		logging.info('Reset wildlife spawn clock: %s' % WORLD_INFO['wildlife_spawn_interval'][0])
	
	cache.scan_cache()
	
def is_night():
	if WORLD_INFO['time_of_day'] == 'night':
		return True
	
	return False

def time_until_midnight():
	if is_night():
		return 0
	
	return WORLD_INFO['length_of_day']-WORLD_INFO['real_time_of_day']

def draw_encounter():
	if not LIFE[SETTINGS['controlling']]['encounters']:
		return False
	
	encounters.draw_encounter(LIFE[SETTINGS['controlling']],
		LIFE[SETTINGS['controlling']]['encounters'][0])

def draw_event():
	_event = None
	
	for event in EVENTS:
		if not event['delay']:
			_event = event
			break
	
	if not _event:
		return False
	
	gfx.camera_track(_event['pos'])
	if len(event['text'])>=MAP_WINDOW_SIZE[0]-1:
		_lines = list(_event['text'].partition(','))
		
		if not len(_lines[1]):
			_lines = list(_event['text'].partition('.'))
		
		if len(_lines[1]):
			_lines.pop(1)
		else:
			lines = ['????']
		
	else:
		_lines = [_event['text']]
	
	for line in _lines:
		if len(line)>=MAP_WINDOW_SIZE[0]-1:
			_lines = ['The most annoying error.']
			break	
	
	_i = 0
	for line in _lines:
		_half = len(line)/2
		_x = numbers.clip((MAP_WINDOW_SIZE[0]/2)-_half, 0, MAP_WINDOW_SIZE[0]-len(line)-1)
		
		gfx.blit_string(_x,
			10+_i,
			line,
		    'overlay')
		
		_i += 1
	
	return True

def show_event(text, time=45, delay=0, life=None, item=None, pos=None, priority=False):
	_event = {'text': text, 'time': time, 'delay': delay, 'life': life}
	
	if life:
		_event['pos'] = life['pos']
	elif item:
		_event['pos'] = item['pos']
	elif pos:
		_event['pos'] = pos
	
	if priority:
		EVENTS.insert(0, _event)
	else:
		EVENTS.append(_event)

def show_next_event():
	if not EVENTS:
		return False
	
	EVENTS.pop(0)
	gfx.refresh_view('map')
	
	if not EVENTS:
		life.focus_on(LIFE[SETTINGS['following']])
		return False
	
	return True

def process_events():
	if not EVENTS:
		return False
	
	_event = None
	for event in EVENTS:
		if not event['delay']:
			_event = event
			break
	
	if not _event:
		for event in EVENTS:
			if event['delay']:
				event['delay'] -= 1
	
	if not _event:
		return False
	
	if _event['time']:
		_event['time'] -= 1
		return True
	
	return show_next_event()

def matches(dict1, dict2):
	_break = False
	for key in dict2:
		if not key in dict1 or not dict1[key] == dict2[key]:
			return False
	
	return True