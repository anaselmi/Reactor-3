from globals import *
import life as lfe

import references
import judgement
import movement
import action
import chunks
import speech
import combat
import brain
import items
import sight
import stats
import maps

import logging
import numbers
import random
import time

def _get_need_amount(life, need):
	if need['amount_callback']:
		return need['amount_callback'](life, need)
	
	if need['amount']:
		return need['amount']

def add_needed_item(life, item_match, amount=1, amount_callback=None, satisfy_if=None, satisfy_callback=None):
	life['needs'][str(life['need_id'])] = {'type': 'item',
	                      'match': item_match,
	                      'meet_with': [],
	                      'could_meet_with': [],
	                      'amount': amount,
	                      'amount_callback': amount_callback,
	                      'satisfy_if': satisfy_if,
	                      'satisfy_callback': satisfy_callback}
	
	logging.debug('Added item need: %s' % item_match)
	
	life['need_id'] += 1
	return str(life['need_id']-1)

def delete_needed_item(life, need_id):
	del life['needs'][need_id]
	
	logging.debug('Remove item need: %s' % need_id)

def process(life):
	for need in life['needs'].values():
		if need['type'] == 'item':
			_has_items = []
			_potential_items = []
			
			for item in brain.get_matching_remembered_items(life, need['match'], no_owner=True):
				_potential_items.append(item)
				
			for item in lfe.get_all_inventory_items(life, matches=[need['match']]):
				_has_items.append(item['uid'])
			
			if len(_has_items) >= _get_need_amount(life, need):
				need['meet_with'] = _has_items
			elif _potential_items:
				need['could_meet_with'] = _potential_items
			else:
				need['meet_with'] = []
				need['could_meet_with'] = []

def is_need_met(life, need):
	if need['meet_with']:
		return True
	
	return False

def needs_to_satisfy(life, need):
	return action.execute_small_script(life, need['satisfy_if'])

def can_satisfy(life, need):
	if not is_need_met(life, need):
		return False
	
	return True

def can_potentially_satisfy(life, need):
	return need['could_meet_with']

def satisfy(life, need):
	if action.execute_small_script(life, need['satisfy_if']):
		if need['type'] == 'item':
			_callback = action.execute_small_script(life, need['satisfy_callback'])
			_callback(life, need['meet_with'][0])
			return True
	
	return False

#TODO: Remove reference from dialog and delete
def is_in_need_matches(life, match):
	_matches = []
	
	for root_need in life['needs']:
		for item in root_need['matches']:
			_break = False

			for key in match:
				if not key in item or not item[key] == match[key]:
					_break = True
					break
			
			if _break:
				continue
			
			_matches.append(root_need)
	
	return _matches

def get_matched_needs(life, match):
	_matches = []
	
	for root_need in life['needs']:
		_break = False
		for need in root_need:
			for key in match:
				if not key in need or not need[key] == match[key]:
					_break = True
					break
			
			if _break:
				break
			
			_matches.append(root_need)
	
	return _matches

def _has_inventory_item(life, matches={}):
	return lfe.get_all_inventory_items(life, matches=[matches])

def check_all_needs(life):
	for need in life['needs']:
		need_is_met(life, need)

def need_is_met(life, need):
	_res = []
	
	for meet_callback in need['need_callback']:
		_res.extend(meet_callback(life, matches=need['need']))
	
	need['matches'] = _res
	
	if len(_res)>=need['min_matches']:
		need['num_above_needed'] = (len(_res)-need['min_matches'])+1
		return True
	
	#logging.info('%s is not meeting a need: %s' % (' '.join(life['name']), need['need']))
	need['num_above_needed'] = 0
	return False

def generate_needs(life):
	if stats.desires_weapon(life):
		brain.flag(life, 'no_weapon')
	else:
		brain.unflag(life, 'no_weapon')
	
	if combat.get_weapons(life):
		if not combat.has_usable_weapon(life):
			if not brain.get_flag(life, 'needs_ammo'):
				_n = add_needed_item(life,
				                     {'type': 'bullet', 'owner': None},
				                     satisfy_if=action.make_small_script(function='get_flag',
				                                                         args={'flag': 'needs_ammo'}),
				                     satisfy_callback=action.make_small_script(return_function='pick_up_and_hold_item'))
				brain.flag(life, 'needs_ammo', value=_n)
		

def manage_hands(life):
	for item in [lfe.get_inventory_item(life, item) for item in lfe.get_held_items(life)]:
		_equip_action = {'action': 'equipitem',
				'item': item['uid']}
		
		if len(lfe.find_action(life,matches=[_equip_action])):
			continue
		
		if lfe.can_wear_item(life, item['uid']):
			lfe.add_action(life, _equip_action,
				401,
				delay=lfe.get_item_access_time(life, item['uid']))
			continue
		
		if not 'CAN_WEAR' in item['flags'] and lfe.get_all_storage(life):
			_store_action = {'action': 'storeitem',
				'item': item['uid'],
				'container': lfe.get_all_storage(life)[0]['uid']}
			
			if len(lfe.find_action(life, matches=[_store_action])):
				continue
			
			lfe.add_action(life,_store_action,
				401,
				delay=lfe.get_item_access_time(life, item['uid']))

def manage_inventory(life):
	for item in [lfe.get_inventory_item(life, item) for item in lfe.get_all_unequipped_items(life, check_hands=False)]:
		_equip_action = {'action': 'equipitem',
				'item': item['uid']}
		
		if len(lfe.find_action(life,matches=[_equip_action])):
			continue
		
		if lfe.can_wear_item(life, item):
			lfe.add_action(life,
				_equip_action,
				401,
				delay=lfe.get_item_access_time(life, item))
			continue

def explore_known_chunks(life):
	#Our first order of business is to figure out exactly what we're looking for.
	#There's a big difference between exploring the map looking for a purpose and
	#exploring the map with a purpose. Both will use similar routines but I wager
	#it'll actually be a lot harder to do it without there being some kind of goal
	#to at least start us in the right direction.
	
	#This function will kick in only if the ALife is idling, so looting is handled
	#automatically.
	
	#Note: Determining whether this fuction should run at all needs to be done inside
	#the module itself.
	_chunk_key = brain.retrieve_from_memory(life, 'explore_chunk')
	_chunk = maps.get_chunk(_chunk_key)
	
	if life['path'] and chunks.position_is_in_chunk(lfe.path_dest(life), _chunk_key):
		return True
	
	if chunks.is_in_chunk(life, '%s,%s' % (_chunk['pos'][0], _chunk['pos'][1])):
		life['known_chunks'][_chunk_key]['last_visited'] = WORLD_INFO['ticks']
		return False
	
	if not _chunk['ground']:
		return False
	
	_pos_in_chunk = random.choice(_chunk['ground'])
	lfe.clear_actions(life)
	lfe.add_action(life,{'action': 'move','to': _pos_in_chunk},200)
	return True

def explore_unknown_chunks(life):
	if life['path']:
		return True
	
	#_chunk_key = references.path_along_reference(life, 'buildings')
	
	#if not _chunk_key:
	_chunk_key = references.path_along_reference(life, 'roads')
	
	if not _chunk_key:
		_best_reference = references._find_best_unknown_reference(life, 'roads')['reference']
		if not _best_reference:
			return False
		
		_chunk_key = references.find_nearest_key_in_reference(life, _best_reference, unknown=True)
	
	if not _chunk_key:
		return False
	
	_walkable_area = chunks.get_walkable_areas(_chunk_key)
	if not _walkable_area:
		print 'no walkable area'
		return False
	
	_closest_pos = {'pos': None, 'distance': -1}
	for pos in _walkable_area:
		_distance = numbers.distance(life['pos'], pos)
				
		if _distance <= 1:
			_closest_pos['pos'] = pos
			break
		
		if not _closest_pos['pos'] or _distance<_closest_pos['distance']:
			_closest_pos['pos'] = pos
			_closest_pos['distance'] = _distance
	
	lfe.clear_actions(life)
	lfe.add_action(life,{'action': 'move','to': _closest_pos['pos']},200)
	
	return True
