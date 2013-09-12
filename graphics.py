from globals import *
from tiles import *

import libtcodpy as tcod

import numbers
import random
import numpy
import time
import life

def init_libtcod(terraform=False):
	global MAP_WINDOW, ITEM_WINDOW, CONSOLE_WINDOW, MESSAGE_WINDOW, PREFAB_WINDOW, X_CUTOUT_WINDOW, Y_CUTOUT_WINDOW
	
	tcod.console_init_root(WINDOW_SIZE[0],WINDOW_SIZE[1],WINDOW_TITLE,renderer=RENDERER)
	MAP_WINDOW = tcod.console_new(MAP_WINDOW_SIZE[0],MAP_WINDOW_SIZE[1])
	ITEM_WINDOW = tcod.console_new(ITEM_WINDOW_SIZE[0],ITEM_WINDOW_SIZE[1])
	CONSOLE_WINDOW = tcod.console_new(CONSOLE_WINDOW_SIZE[0],CONSOLE_WINDOW_SIZE[1])
	MESSAGE_WINDOW = tcod.console_new(MESSAGE_WINDOW_SIZE[0],MESSAGE_WINDOW_SIZE[1])
	
	if terraform:
		PREFAB_WINDOW = tcod.console_new(PREFAB_WINDOW_SIZE[0],PREFAB_WINDOW_SIZE[1])
		X_CUTOUT_WINDOW = tcod.console_new(X_CUTOUT_WINDOW_SIZE[0],X_CUTOUT_WINDOW_SIZE[1])
		Y_CUTOUT_WINDOW = tcod.console_new(Y_CUTOUT_WINDOW_SIZE[0],Y_CUTOUT_WINDOW_SIZE[1])
		
		PREFAB_CHAR_BUFFER[0] = numpy.zeros((PREFAB_WINDOW_SIZE[1], PREFAB_WINDOW_SIZE[0]), dtype=numpy.int8)
		PREFAB_CHAR_BUFFER[1] = numpy.zeros((PREFAB_WINDOW_SIZE[1], PREFAB_WINDOW_SIZE[0]), dtype=numpy.int8)
		X_CUTOUT_CHAR_BUFFER[0] = numpy.zeros((X_CUTOUT_WINDOW_SIZE[1], X_CUTOUT_WINDOW_SIZE[0]), dtype=numpy.int8)
		X_CUTOUT_CHAR_BUFFER[1] = numpy.zeros((X_CUTOUT_WINDOW_SIZE[1], X_CUTOUT_WINDOW_SIZE[0]), dtype=numpy.int8)
		Y_CUTOUT_CHAR_BUFFER[0] = numpy.zeros((Y_CUTOUT_WINDOW_SIZE[1], Y_CUTOUT_WINDOW_SIZE[0]), dtype=numpy.int8)
		Y_CUTOUT_CHAR_BUFFER[1] = numpy.zeros((Y_CUTOUT_WINDOW_SIZE[1], Y_CUTOUT_WINDOW_SIZE[0]), dtype=numpy.int8)
	
	tcod.console_set_custom_font(FONT,FONT_LAYOUT)
	tcod.console_set_keyboard_repeat(200, 0)
	tcod.sys_set_fps(FPS)

	for i in range(3):
		MAP_RGB_BACK_BUFFER[i] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]))
		MAP_RGB_FORE_BUFFER[i] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]))
		RGB_LIGHT_BUFFER[i] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]), dtype=numpy.int8)
		
		if terraform:
			PREFAB_RGB_BACK_BUFFER[i] = numpy.zeros((PREFAB_WINDOW_SIZE[1], PREFAB_WINDOW_SIZE[0]), dtype=numpy.int8)
			PREFAB_RGB_FORE_BUFFER[i] = numpy.zeros((PREFAB_WINDOW_SIZE[1], PREFAB_WINDOW_SIZE[0]), dtype=numpy.int8)
			X_CUTOUT_RGB_BACK_BUFFER[i] = numpy.zeros((X_CUTOUT_WINDOW_SIZE[1], X_CUTOUT_WINDOW_SIZE[0]), dtype=numpy.int8)
			X_CUTOUT_RGB_FORE_BUFFER[i] = numpy.zeros((X_CUTOUT_WINDOW_SIZE[1], X_CUTOUT_WINDOW_SIZE[0]), dtype=numpy.int8)
			Y_CUTOUT_RGB_BACK_BUFFER[i] = numpy.zeros((Y_CUTOUT_WINDOW_SIZE[1], Y_CUTOUT_WINDOW_SIZE[0]), dtype=numpy.int8)
			Y_CUTOUT_RGB_FORE_BUFFER[i] = numpy.zeros((Y_CUTOUT_WINDOW_SIZE[1], Y_CUTOUT_WINDOW_SIZE[0]), dtype=numpy.int8)
	
	LOS_BUFFER[0] = []
	MAP_CHAR_BUFFER[0] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]), dtype=numpy.int8)
	MAP_CHAR_BUFFER[1] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]), dtype=numpy.int8)
	DARK_BUFFER[0] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]), dtype=numpy.int8)
	LIGHT_BUFFER[0] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]), dtype=numpy.int8)

def start_of_frame(draw_char_buffer=True):
	tcod.console_fill_background(MAP_WINDOW,
	        numpy.subtract(numpy.add(numpy.subtract(MAP_RGB_BACK_BUFFER[0],RGB_LIGHT_BUFFER[0]),LIGHT_BUFFER[0]),DARK_BUFFER[0]).clip(0,255),
	        numpy.subtract(numpy.add(numpy.subtract(MAP_RGB_BACK_BUFFER[1],RGB_LIGHT_BUFFER[1]),LIGHT_BUFFER[0]),DARK_BUFFER[0]).clip(0,255),
	        numpy.subtract(numpy.add(numpy.subtract(MAP_RGB_BACK_BUFFER[2],RGB_LIGHT_BUFFER[2]),LIGHT_BUFFER[0]),DARK_BUFFER[0]).clip(0,255))
	tcod.console_fill_foreground(MAP_WINDOW,
	        numpy.subtract(numpy.add(numpy.subtract(MAP_RGB_FORE_BUFFER[0],RGB_LIGHT_BUFFER[0]),LIGHT_BUFFER[0]),DARK_BUFFER[0]).clip(0,255),
	        numpy.subtract(numpy.add(numpy.subtract(MAP_RGB_FORE_BUFFER[1],RGB_LIGHT_BUFFER[1]),LIGHT_BUFFER[0]),DARK_BUFFER[0]).clip(0,255),
	        numpy.subtract(numpy.add(numpy.subtract(MAP_RGB_FORE_BUFFER[2],RGB_LIGHT_BUFFER[2]),LIGHT_BUFFER[0]),DARK_BUFFER[0]).clip(0,255))
	
	if draw_char_buffer:
		tcod.console_fill_char(MAP_WINDOW,MAP_CHAR_BUFFER[0])

def start_of_frame_terraform():
	tcod.console_fill_background(PREFAB_WINDOW,PREFAB_RGB_BACK_BUFFER[0],PREFAB_RGB_BACK_BUFFER[1],PREFAB_RGB_BACK_BUFFER[2])
	tcod.console_fill_foreground(PREFAB_WINDOW,PREFAB_RGB_FORE_BUFFER[0],PREFAB_RGB_FORE_BUFFER[1],PREFAB_RGB_FORE_BUFFER[2])
	tcod.console_fill_char(PREFAB_WINDOW,PREFAB_CHAR_BUFFER[0])
	
	tcod.console_fill_background(X_CUTOUT_WINDOW,X_CUTOUT_RGB_BACK_BUFFER[0],X_CUTOUT_RGB_BACK_BUFFER[1],X_CUTOUT_RGB_BACK_BUFFER[2])
	tcod.console_fill_foreground(X_CUTOUT_WINDOW,X_CUTOUT_RGB_FORE_BUFFER[0],X_CUTOUT_RGB_FORE_BUFFER[1],X_CUTOUT_RGB_FORE_BUFFER[2])
	tcod.console_fill_char(X_CUTOUT_WINDOW,X_CUTOUT_CHAR_BUFFER[0])
	
	tcod.console_fill_background(Y_CUTOUT_WINDOW,Y_CUTOUT_RGB_BACK_BUFFER[0],Y_CUTOUT_RGB_BACK_BUFFER[1],Y_CUTOUT_RGB_BACK_BUFFER[2])
	tcod.console_fill_foreground(Y_CUTOUT_WINDOW,Y_CUTOUT_RGB_FORE_BUFFER[0],Y_CUTOUT_RGB_FORE_BUFFER[1],Y_CUTOUT_RGB_FORE_BUFFER[2])
	tcod.console_fill_char(Y_CUTOUT_WINDOW,Y_CUTOUT_CHAR_BUFFER[0])

def refresh_window_position(x, y):
	DARK_BUFFER[0][y,x] = 0
	LIGHT_BUFFER[0][y,x] = 0
	MAP_CHAR_BUFFER[1][y,x] = 0

def refresh_window():
	#DARK_BUFFER[0] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]))
	#LIGHT_BUFFER[0] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]))
	MAP_CHAR_BUFFER[1] = numpy.zeros((MAP_WINDOW_SIZE[1], MAP_WINDOW_SIZE[0]))

def blit_tile_to_console(console, x, y, tile):
	_tile = get_raw_tile(tile)
	
	tcod.console_put_char_ex(console, x, y, _tile['icon'], _tile['color'][0], _tile['color'][1])

def blit_tile(x,y,tile,char_buffer=MAP_CHAR_BUFFER,rgb_fore_buffer=MAP_RGB_FORE_BUFFER,rgb_back_buffer=MAP_RGB_BACK_BUFFER):
	_tile = get_raw_tile(tile)

	blit_char(x,y,_tile['icon'],
		_tile['color'][0],
		_tile['color'][1],
		char_buffer=char_buffer,
		rgb_fore_buffer=rgb_fore_buffer,
		rgb_back_buffer=rgb_back_buffer)

def blit_char(x,y,char,fore_color=None,back_color=None,char_buffer=None,rgb_fore_buffer=None,rgb_back_buffer=None):
	if fore_color:
		rgb_fore_buffer[0][y,x] = fore_color.r
		rgb_fore_buffer[1][y,x] = fore_color.g
		rgb_fore_buffer[2][y,x] = fore_color.b

	if back_color:
		rgb_back_buffer[0][y,x] = back_color.r
		rgb_back_buffer[1][y,x] = back_color.g
		rgb_back_buffer[2][y,x] = back_color.b

	char_buffer[0][y,x] = ord(char)
	char_buffer[1][y,x] = 1

def blit_string(x, y, text, console=0, fore_color=tcod.white, back_color=None, flicker=0):
	i = 0
	
	for c in text:
		_back_color = back_color
		
		#if not _back_color:
			#_back_color = Color(int(MAP_RGB_BACK_BUFFER[0][y,x+i])+random.randint(0,flicker),
			#	int(MAP_RGB_BACK_BUFFER[1][y,x+i]+random.randint(0,flicker)),
			#	int(MAP_RGB_BACK_BUFFER[2][y,x+i]+random.randint(0,flicker)))
		
		#_alpha = int(LIGHT_BUFFER[0][y,x+i])
		
		blit_char(x+i,
			y,
			c,
			fore_color=fore_color,
			back_color=_back_color,
			char_buffer=MAP_CHAR_BUFFER,
			rgb_fore_buffer=MAP_RGB_FORE_BUFFER,
			rgb_back_buffer=MAP_RGB_BACK_BUFFER)
		
		darken_tile(x+i,y,0)
		lighten_tile(x+i,y,0)
		i+=1

def darken_tile(x,y,amt):
	DARK_BUFFER[0][y,x] = amt

def lighten_tile(x,y,amt):
	LIGHT_BUFFER[0][y,x] = amt

def tint_tile(x,y,color,coef):
	_o_color = tcod.Color(int(MAP_RGB_BACK_BUFFER[0][y,x]),int(MAP_RGB_BACK_BUFFER[1][y,x]),int(MAP_RGB_BACK_BUFFER[2][y,x]))
	_n_color = tcod.color_lerp(_o_color,color,coef)
	
	MAP_RGB_BACK_BUFFER[0][y,x] = _n_color.r
	MAP_RGB_BACK_BUFFER[1][y,x] = _n_color.g
	MAP_RGB_BACK_BUFFER[2][y,x] = _n_color.b

def fade_to_white(amt):
	amt = int(round(amt))
	
	if amt > 255:
		amt = 255
	
	for x in range(MAP_WINDOW_SIZE[0]):
		for y in range(MAP_WINDOW_SIZE[1]):
			darken_tile(x,y,0)
			lighten_tile(x,y,amt)

def draw_cursor(cursor,camera,tile,char_buffer=MAP_CHAR_BUFFER,rgb_fore_buffer=MAP_RGB_FORE_BUFFER,rgb_back_buffer=MAP_RGB_BACK_BUFFER):
	if time.time()%1>=0.5:
		blit_char(cursor[0]-camera[0],
			cursor[1]-camera[1],
			'X',
			tcod.white,
			tcod.black,
			char_buffer=char_buffer,
			rgb_fore_buffer=rgb_fore_buffer,
			rgb_back_buffer=rgb_back_buffer)
	else:
		blit_tile(cursor[0]-camera[0],
			cursor[1]-camera[1],
			tile,
			char_buffer=char_buffer,
			rgb_fore_buffer=rgb_fore_buffer,
			rgb_back_buffer=rgb_back_buffer)

def draw_bottom_ui_terraform():
	"""Controls the drawing of the UI under the map."""
	
	_string = '%s fps ' % str(tcod.sys_get_fps())
	_string += 'X: %s Y: %s Z: %s' % (MAP_CURSOR[0],MAP_CURSOR[1],CAMERA_POS[2])
	
	blit_string(MAP_WINDOW_SIZE[0]-len(_string),
		MAP_WINDOW_SIZE[1]-1,
		_string,
		console=MAP_WINDOW,
		fore_color=tcod.Color(255,255,255),
		back_color=tcod.Color(0,0,0),
		flicker=0)

def draw_message_box():	
	tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.Color(128,128,128))
	tcod.console_print_frame(MESSAGE_WINDOW,0,0,MESSAGE_WINDOW_SIZE[0],MESSAGE_WINDOW_SIZE[1])
	tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.white)
	tcod.console_print(MESSAGE_WINDOW,1,0,'Messages')
	
	_y_mod = 1
	_lower = numbers.clip(0,len(MESSAGE_LOG)-MESSAGE_LOG_MAX_LINES,100000)
	for msg in MESSAGE_LOG[_lower:len(MESSAGE_LOG)]:
		if msg['count']:
			_text = '%s (x%s)' % (msg['msg'], msg['count']+1)
		else:		
			_text = msg['msg']
		
		if msg['style'] == 'damage':
			tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.red)
		elif msg['style'] == 'speech':
			tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.gray)
		elif msg['style'] == 'action':
			tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.lighter_crimson)
		elif msg['style'] == 'important':
			tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.Color(150,150,255))
		elif msg['style'] == 'radio':
			tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.Color(225,245,169))
		elif msg['style'] == 'good':
			tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.light_green)
		elif msg['style'] == 'player_combat_good':
			tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.green)
		elif msg['style'] == 'player_combat_bad':
			tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.crimson)
		else:
			tcod.console_set_default_foreground(MESSAGE_WINDOW, tcod.white)
		
		tcod.console_print(MESSAGE_WINDOW, 1, _y_mod, _text)
		_y_mod += 1

def draw_status_line():
	_flashing_text = ''
	_non_flashing_text = ''
	
	if LIFE[SETTINGS['following']]['targeting']:
		_flashing_text += 'Firing'
	
	if LIFE[SETTINGS['following']]['strafing']:
		_non_flashing_text += 'Strafing'
	
	if life.is_target_of(LIFE[SETTINGS['following']]):
		_flashing_text += 'Combat'
	
	blit_string(0,
		MAP_WINDOW_SIZE[1]-1,
		_non_flashing_text)
	
	if time.time()%1>=0.5:
		blit_string(len(_non_flashing_text)+1,
			MAP_WINDOW_SIZE[1]-1,
			_flashing_text)

def draw_selected_tile_in_item_window(pos):
	if time.time()%1>=0.5:
		tcod.console_print(ITEM_WINDOW,pos,0,chr(15))

def draw_all_tiles():
	for tile in TILES:
		tcod.console_set_char_foreground(ITEM_WINDOW, TILES.keys().index(tile), 0, TILES[tile]['color'][0])
		tcod.console_set_char_background(ITEM_WINDOW, TILES.keys().index(tile), 0, TILES[tile]['color'][1])
		tcod.console_set_char(ITEM_WINDOW, TILES.keys().index(tile), 0, TILES[tile]['icon'])

def draw_dijkstra_heatmap():
	if not SETTINGS['heatmap']:
		return False
	
	_map = SETTINGS['heatmap']
	
	for _x in range(_map['x_range'][0],_map['x_range'][1]):		
		x = _x-_map['x_range'][0]
		
		if x<0 or x>=MAP_WINDOW_SIZE[0]:
			continue
		
		for _y in range(_map['y_range'][0],_map['y_range'][1]):			
			y = _y-_map['y_range'][0]
			
			if y<CAMERA_POS[1] or y>=MAP_WINDOW_SIZE[1]:
				continue
			
			_score = abs(SETTINGS['heatmap']['map'][_x][_y])/8
			_light = numbers.clip(_score,0,150)
			lighten_tile(x,y,_light)

def draw_chunk_map():
	for y in range(0, MAP_SIZE[1], WORLD_INFO['chunk_size']):
		for x in range(0, MAP_SIZE[0], WORLD_INFO['chunk_size']):
			_type = WORLD_INFO['chunk_map']['%s,%s' % (x, y)]['type']
			_tile = str(_type[0])
			
			if _type == 'other':
				_fore_color = tcod.Color(15, 15, 15)
				_tile = '/'
			elif _type == 'factory':
				_fore_color = tcod.gray
			elif _type == 'forest':
				_fore_color = tcod.darker_green
			elif _type == 'town':
				_fore_color = tcod.brass
			elif _type == 'road':
				_fore_color = tcod.light_gray
			else:
				_fore_color = tcod.white
			
			if MAP_CURSOR[0]/WORLD_INFO['chunk_size'] == x/WORLD_INFO['chunk_size'] and MAP_CURSOR[1]/WORLD_INFO['chunk_size'] == y/WORLD_INFO['chunk_size']:
				_fore_color = tcod.white
				_tile = 'x'
			
			blit_char(x/WORLD_INFO['chunk_size'],
			          y/WORLD_INFO['chunk_size'],
			          _tile,
			          char_buffer=MAP_CHAR_BUFFER,
			          fore_color=_fore_color,
			          back_color=tcod.black,
			          rgb_fore_buffer=MAP_RGB_FORE_BUFFER,
			          rgb_back_buffer=MAP_RGB_BACK_BUFFER)

def draw_console():
	if not SETTINGS['draw console']:
		return False
	
	tcod.console_rect(CONSOLE_WINDOW,0,0,CONSOLE_WINDOW_SIZE[0],CONSOLE_WINDOW_SIZE[1],True,flag=tcod.BKGND_DEFAULT)
	
	_i = 0
	for line in CONSOLE_HISTORY[len(CONSOLE_HISTORY)-CONSOLE_HISTORY_MAX_LINES:]:
		_xoffset = 0
		
		if CONSOLE_HISTORY.index(line) % 2:
			tcod.console_set_default_foreground(CONSOLE_WINDOW, tcod.Color(185,185,185))
		else:
			tcod.console_set_default_foreground(CONSOLE_WINDOW, tcod.white)
		
		while len(line):
			tcod.console_print(CONSOLE_WINDOW,_xoffset,_i,line[:CONSOLE_WINDOW_SIZE[0]])
			line = line[CONSOLE_WINDOW_SIZE[0]:]
			_xoffset += 1
			_i += 1
			
	tcod.console_print(CONSOLE_WINDOW,0,CONSOLE_WINDOW_SIZE[1]-1,'#'+KEYBOARD_STRING[0])

def log(text):
	CONSOLE_HISTORY.append(text)

def message(text, style=None):
	if MESSAGE_LOG and MESSAGE_LOG[len(MESSAGE_LOG)-1]['msg'] == text:
		MESSAGE_LOG[len(MESSAGE_LOG)-1]['count'] += 1
		return None
	
	MESSAGE_LOG.append({'msg': text, 'style': style, 'count': 0})

def radio(source, text):
	message('%s: %s' % (' '.join(source['name']), text), style='radio')

def title(text, padding=2, text_color=tcod.white, background_color=tcod.black):
	_center_x = (WINDOW_SIZE[0]/2)-len(text)/2
	_center_y = WINDOW_SIZE[1]/2
	tcod.console_set_default_background(0, background_color)
	tcod.console_set_default_foreground(0, text_color)
	tcod.console_print_frame(0,
	                         _center_x-padding,
	                         _center_y-padding,
	                         len(text)+padding*2,
	                         1+padding*2,
	                         flag=tcod.BKGND_SET,
	                         clear=True)
	tcod.console_print(0, _center_x, _center_y, text)
	tcod.console_flush()

def position_is_in_frame(pos):
	if pos[0] >= CAMERA_POS[0] and pos[0] <= CAMERA_POS[0]+MAP_WINDOW_SIZE[0] and \
	   pos[1] >= CAMERA_POS[1] and pos[1] <= CAMERA_POS[1]+MAP_WINDOW_SIZE[1]:
		return True
	
	return False

def get_render_position(pos):
	return [pos[0]-CAMERA_POS[0], pos[1]-CAMERA_POS[1]]

def end_of_frame_terraform(editing_prefab=False, draw_cutouts=True):
	tcod.console_blit(ITEM_WINDOW,0,0,ITEM_WINDOW_SIZE[0],ITEM_WINDOW_SIZE[1],0,0,MAP_WINDOW_SIZE[1])
	
	if draw_cutouts:
		tcod.console_blit(PREFAB_WINDOW,
			0,
			0,
			PREFAB_WINDOW_SIZE[0],
			PREFAB_WINDOW_SIZE[1],
			0,
			PREFAB_WINDOW_OFFSET[0],
			PREFAB_WINDOW_OFFSET[1])
		tcod.console_blit(X_CUTOUT_WINDOW,
			0,
			0,
			X_CUTOUT_WINDOW_SIZE[0],
			X_CUTOUT_WINDOW_SIZE[1],
			0,
			PREFAB_WINDOW_OFFSET[0],
			11)
		tcod.console_blit(Y_CUTOUT_WINDOW,
			0,
			0,
			Y_CUTOUT_WINDOW_SIZE[0],
			Y_CUTOUT_WINDOW_SIZE[1],
			0,
			PREFAB_WINDOW_OFFSET[0],
			22)
	
	if editing_prefab:
		tcod.console_set_default_foreground(0, tcod.white)
	else:
		tcod.console_set_default_foreground(0, tcod.Color(185,185,185))
	
	#TODO: Figure these out using math
	tcod.console_print(0,PREFAB_WINDOW_OFFSET[0],0,'Prefab Editor')
	tcod.console_print(0,PREFAB_WINDOW_OFFSET[0],11,'West -X Cutout- East')
	tcod.console_print(0,PREFAB_WINDOW_OFFSET[0],25,'North -Y Cutout- South')

def end_of_frame_reactor3():
	tcod.console_blit(MESSAGE_WINDOW,0,0,MESSAGE_WINDOW_SIZE[0],MESSAGE_WINDOW_SIZE[1],0,0,MAP_WINDOW_SIZE[1])

def end_of_frame(draw_map=True):
	if not SETTINGS['map_slices'] and draw_map:
		tcod.console_blit(MAP_WINDOW,0,0,MAP_WINDOW_SIZE[0],MAP_WINDOW_SIZE[1],0,0,0)
	
	_encounter = None
	if SETTINGS['controlling'] and LIFE[SETTINGS['controlling']]['encounters']:
		_encounter = LIFE[SETTINGS['controlling']]['encounters'][0]
	
	if _encounter and 'console' in _encounter:
		tcod.console_blit(_encounter['console'], 0, 0,
			40,
			40,
			0,
			0,
			0,
			1, 0.5)
	
	_dialog = None
	if SETTINGS['controlling'] and LIFE[SETTINGS['controlling']]['dialogs']:
		_dialog = LIFE[SETTINGS['controlling']]['dialogs'][0]
	
	if _dialog and 'console' in _dialog:
		tcod.console_blit(_dialog['console'], 0, 0,
			WINDOW_SIZE[0],
			40,
			0,
			0,
			0,
			1, 0.9)
	
	for menu in MENUS:
		tcod.console_blit(menu['settings']['console'],0,0,
			menu['settings']['size'][0],
			menu['settings']['size'][1],0,
			menu['settings']['position'][0],
			menu['settings']['position'][1],1,0.5)
		
	if SETTINGS['draw console']:
		tcod.console_blit(CONSOLE_WINDOW,0,0,CONSOLE_WINDOW_SIZE[0],CONSOLE_WINDOW_SIZE[1],0,0,0,1,0.5)
	
	tcod.console_flush()

def window_is_closed():
	return tcod.console_is_window_closed()
