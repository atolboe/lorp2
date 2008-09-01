"""Main user interface module for the project. Contains all drawing and input 
routines."""

import curses
import time
import sys

from GameObjects import Player

curr_player = None

def init_ui():
	"""The first function to call in order to initialize the screen."""
	# Use wrapper to set reasonable defaults and reset the terminal on exit
	#curses.wrapper(_main_loop)
	curses.wrapper(_init_func)

def _init_func(scr):
	curses.curs_set(0)
	scr.nodelay(1)	# Make getch() non-blocking
	curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLUE)
	curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
	curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLUE)
	_main_loop(scr)

def _main_loop(scr):
	"""Main logic goes here."""
	global curr_player
	bob = Player()
	bob.name = 'Bob'
	curr_player = bob

	while 1:
		# Keep player in bounds (should actually change maps)
		if bob.map_coords[0] > 79:
			bob.map_coords[0] = 0
		if bob.map_coords[0] < 0:
			bob.map_coords[0] = 79
		if bob.map_coords[1] > 19:
			bob.map_coords[1] = 0
		if bob.map_coords[1] < 0:
			bob.map_coords[1] = 19
		time.sleep(0.01)

		scr.erase()
		scr.addstr(bob.map_coords[1], bob.map_coords[0], '@')

		_draw_info_area(scr)
		_handle_input(scr)

def _draw_info_area(scr):
	loc_str = 'Location is '
	loc = 'Nowhere'
	scr.attrset(curses.color_pair(1))
	scr.addstr(20, 3, loc_str)
	scr.addstr(loc, curses.color_pair(1) | curses.A_BOLD)
	scr.addstr('. HP: (')
	scr.addstr(str(curr_player.hitpoints), curses.color_pair(2) | curses.A_BOLD)
	scr.addstr(' of ')
	scr.addstr(str(curr_player.hitpoints), curses.color_pair(2) | curses.A_BOLD)
	scr.addstr(').')
	for i in range(scr.getyx()[1], 79 - 19):
		scr.addstr(' ')
	scr.addstr(20, 79 - 19, ' Press ')
	scr.addstr('?', curses.color_pair(2) | curses.A_BOLD)
	scr.addstr(' for help. ')

	scr.addstr(24, 0, 'SYSOP', curses.color_pair(3) | curses.A_BOLD)
	title = 'LORP II: New World - Node 0'
	title_x = (79 / 2) - (len(title) / 2)
	for i in range(scr.getyx()[1], title_x):
		scr.addstr(' ')
	scr.addstr(title, curses.color_pair(1) | curses.A_BOLD)
	for i in range(scr.getyx()[1], 79 - 8):
		scr.addstr(' ')
	scr.addstr('118:29', curses.color_pair(2) | curses.A_BOLD)
	for i in range(scr.getyx()[1], 79):
		scr.addstr(' ')

	scr.attrset(0) # Reset drawing attributes

def _handle_input(scr):
	ch = scr.getch()
	if ch == ord('q'):
		sys.exit(0)
	if ch == ord('j'):
		curr_player.map_coords[1] += 1
	if ch == ord('k'):
		curr_player.map_coords[1] -= 1
	if ch == ord('h'):
		curr_player.map_coords[0] -= 1
	if ch == ord('l'):
		curr_player.map_coords[0] += 1

if __name__ == '__main__':
	init_ui()
