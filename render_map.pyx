from tiles import *
import graphics as gfx
import time

VERSION = 4

def render_map(map):
	cdef int _CAMERA_POS[2]
	cdef int _MAP_SIZE[2]
	cdef int _MAP_WINDOW_SIZE[2]
	_CAMERA_POS[0] = CAMERA_POS[0]
	_CAMERA_POS[1] = CAMERA_POS[1]
	_CAMERA_POS[2] = CAMERA_POS[2]
	_MAP_SIZE[0] = MAP_SIZE[0]
	_MAP_SIZE[1] = MAP_SIZE[1]
	_MAP_SIZE[2] = MAP_SIZE[2]
	_MAP_WINDOW_SIZE[0] = MAP_WINDOW_SIZE[0]
	_MAP_WINDOW_SIZE[1] = MAP_WINDOW_SIZE[1]
	
	cdef int x, y, z
	cdef int _X_MAX = _CAMERA_POS[0]+_MAP_WINDOW_SIZE[0]
	cdef int _Y_MAX = _CAMERA_POS[1]+_MAP_WINDOW_SIZE[1]
	cdef int _X_START = _CAMERA_POS[0]
	cdef int _Y_START = _CAMERA_POS[1]
	cdef int _RENDER_X = 0
	cdef int _RENDER_Y = 0
	
	DARK_BUFFER[0] = numpy.zeros((_MAP_WINDOW_SIZE[1], _MAP_WINDOW_SIZE[0]))
	LIGHT_BUFFER[0] = numpy.zeros((_MAP_WINDOW_SIZE[1], _MAP_WINDOW_SIZE[0]))

	if _X_MAX>_MAP_SIZE[0]:
		_X_MAX = _MAP_SIZE[0]

	if _Y_MAX>_MAP_SIZE[1]:
		_Y_MAX = _MAP_SIZE[1]

	for x in range(_X_START,_X_MAX):
		_RENDER_X = x-_CAMERA_POS[0]
		for y in range(_Y_START,_Y_MAX):
			_RENDER_Y = y-_CAMERA_POS[1]
			_drawn = False
			for z in range(MAP_SIZE[2]-1,-1,-1):
				if map[x][y][z]:
					if z > _CAMERA_POS[2] and SETTINGS['draw z-levels above'] and not LOS_BUFFER[0][_RENDER_Y,_RENDER_X]:
						gfx.blit_tile(_RENDER_X,_RENDER_Y,map[x][y][z])
						gfx.darken_tile(_RENDER_X,_RENDER_Y,abs((_CAMERA_POS[2]-z))*30)
						_drawn = True
					elif z == _CAMERA_POS[2]:
						if (x,y,z) in SELECTED_TILES[0] and time.time()%1>=0.5:
							gfx.blit_char(_RENDER_X,
								_RENDER_Y,
								'X',
								darker_grey,
								black,
								char_buffer=MAP_CHAR_BUFFER,
								rgb_fore_buffer=MAP_RGB_FORE_BUFFER,
								rgb_back_buffer=MAP_RGB_BACK_BUFFER)
						else:
							gfx.blit_tile(_RENDER_X,_RENDER_Y,map[x][y][z])
						_drawn = True
					elif z < _CAMERA_POS[2] and SETTINGS['draw z-levels below']:
						gfx.blit_tile(_RENDER_X,_RENDER_Y,map[x][y][z])
						gfx.darken_tile(_RENDER_X,_RENDER_Y,abs((_CAMERA_POS[2]-z))*30)
						_drawn = True
				
					if SETTINGS['draw z-levels above'] and _drawn:
						break
			
			if not _drawn:
				gfx.blit_tile(_RENDER_X,_RENDER_Y,BLANK_TILE)
