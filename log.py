#╔════════════╤══════════════════════════════════════╗
#║Author      │Carsen Yates                          ║
#╟────────────┼──────────────────────────────────────╢
#║Date created│04/23/2017                            ║
#╟────────────┼──────────────────────────────────────╢
#║Description │For making terminal output look pretty║
#╚════════════╧══════════════════════════════════════╝

import sys
from config import *
from enum import ENUM

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
CYAN  = "\033[1;36m"
MAGENTA  = "\033[1;35m"

def remove_formats(string):
	for f in [HEADER, OKBLUE, OKGREEN, WARNING, FAIL, ENDC, BOLD, UNDERLINE, CYAN, MAGENTA]:
		string = string.replace(f, '')
	return string

# Formats a string for the terminal, format options are above
# returns a string
def format(string, f):
	if not COLORED_LOG_MESSAGES:
		return string
	return f + string + ENDC

def count_lines(string):
	return len(string.split('\n'))
	

#╔═╤═╗
#║1│2║
#╟─┼─╢
#║3│4║
#╚═╧═╝
# Turns a 2D array of strings into a string that is formatted into a box matrix like above
# This is a FUCKING masterpiece.  I wrote it for the pure fun of it
def get_box(box):
	result = '╔'

	# First we have to get the sizes of each box
	col_widths = []
	row_heights = []
	for i in box[0]:
		col_widths.append(0)
	for i in range(0, len(box)):
		row_heights.append(0)
	for i in range(0, len(box)):
		for j in range(0, len(box[i])):
			rf = remove_formats(str(box[i][j]))
			lines = rf.split('\n')
			length = len(lines)
			if length > row_heights[i]:
				row_heights[i] = length
			for line in lines:
				l = len(line)
				if l > col_widths[j]:
					col_widths[j] =  l
			
	# now lets print that shit
	for i in range(0, len(box)):
		x = box[i]
		# First we print the edge of the table that is above the current row
		if i == 0: # The top edge
			for j in range(0, len(x)):
				for k in range(0, col_widths[j]):
					result += ('═');
				if j == (len(x) - 1):
					result += ('╗\n')
				else:
					result += ('╤')
		else: # row separator
			result += ('╟')
			for j in range(0, len(x)):
				for k in range(0, col_widths[j]):
					result += ('─');
				if j == (len(x) - 1):
					result += ('╢\n')
				else:
					result += ('┼')

		# now we print the current row
		# NEW
		y = []
		for j in range(0, len(x)):
			y.append(str(x[j]).split('\n'))
		for k in range(0, row_heights[i]): # LINE
			result += ('║')
			for j in range(0, len(x)): # COLUMN
				numlines = len(y[j])
				c = 0
				if k < numlines:
					z = str(y[j][k])
					result += z
					c += len(remove_formats(z))
				for q in range(c, col_widths[j]):
					result += ' '

				if j == (len(x) - 1):
					result += ('║\n')
				else:
					result += ('│')

		# now print the bottom part of the table
		if i == (len(box) - 1):
			result += ('╚')
			for j in range(0, len(x)):
				for k in range(0, col_widths[j]):
					result += ('═');
				if j == (len(x) - 1):
					result += ('╝\n')
				else:
					result += ('╧')
	return result

# Turns a 2D array of strings into a string that is formatted into a box matrix like above
# This is a FUCKING masterpiece.  I wrote it for the pure fun of it
def get_boxf(box, text_format, box_format):
	if not COLORED_LOG_MESSAGES:
		return get_box(box)
	result = format('╔',box_format)

	# First we have to get the sizes of each box
	col_widths = []
	row_heights = []
	for i in box[0]:
		col_widths.append(0)
	for i in range(0, len(box)):
		row_heights.append(0)
	for i in range(0, len(box)):
		for j in range(0, len(box[i])):
			rf = remove_formats(str(box[i][j]))
			lines = rf.split('\n')
			length = len(lines)
			if length > row_heights[i]:
				row_heights[i] = length
			for line in lines:
				l = len(line)
				if l > col_widths[j]:
					col_widths[j] =  l
			
	# now lets print that shit
	for i in range(0, len(box)):
		x = box[i]
		# First we print the edge of the table that is above the current row
		if i == 0: # The top edge
			for j in range(0, len(x)):
				result += box_format
				for k in range(0, col_widths[j]):
					result += ('═');
				if j == (len(x) - 1):
					result += ('╗'+ENDC+'\n')
				else:
					result += ('╤')
		else: # row separator
			result += (box_format + '╟')
			for j in range(0, len(x)):
				for k in range(0, col_widths[j]):
					result += ('─');
				if j == (len(x) - 1):
					result += ('╢'+ENDC+'\n')
				else:
					result += ('┼')

		# now we print the current row
		# NEW
		y = []
		for j in range(0, len(x)):
			y.append(str(x[j]).split('\n'))
		for k in range(0, row_heights[i]): # LINE
			result += format('║', box_format)
			for j in range(0, len(x)): # COLUMN
				numlines = len(y[j])
				c = 0
				if k < numlines:
					z = str(y[j][k])
					result += format(z, text_format)
					c += len(remove_formats(z))
				for q in range(c, col_widths[j]):
					result += ' '

				if j == (len(x) - 1):
					result += (format('║', box_format)+'\n')
				else:
					result += format('│', box_format)			
			
				

		# now print the bottom part of the table
		if i == (len(box) - 1):
			result += (box_format+'╚')
			for j in range(0, len(x)):
				for k in range(0, col_widths[j]):
					result += ('═');
				if j == (len(x) - 1):
					result += ('╝'+ENDC+'\n')
				else:
					result += ('╧')
	return result

# prints a string without a newline
def s_print(string):
	sys.stdout.write(string)
	sys.stdout.flush()
	
# takes a 2D array of strings and prints it in the console magically
def box(box):
	s_print(get_box(box))

# takes a 2D array of strings and prints it in the console magically
def boxf(box, text_format, box_format):
	s_print(get_boxf(box, text_format, box_format))

# Prints a string inside a box
def rect(string):
	box([[string]])

# Formats a string and prints it inside a box
def rectf(string , f):
	if not COLORED_LOG_MESSAGES:
		return rect(string)
	return rect(format(string, f))

class Level(enum):
	INFO=1
	DEBUG=2
	SOCKET_IN=3
	SOCKET_OUT=4
	WARNING=5
	ERROR=6
	
DEBUG_FORMATTING = BOLD
	
def log(level, tag, event):
	if not isinstance(level, Level):
		log(Level.ERROR, "Logger","Param 'level' was not an instance of log.Level")
	if COLORED_LOG_MESSAGES:
		box_color = OKBLUE
		text_format = BOLD
		if Level.DEBUG == level:
			box_color = OKGREEN
		if Level.WARNING == level:
			box_color = WARNING
		if Level.ERROR == level:
			box_color = FAIL;
			
		s_print(get_boxf([[level.name],[tag],[event]], text_format, box_color));
	else:
		s_print(level.name)
		s_print(": ")
		s_print(tag)
		s_print(": ")
		s_print(event)
		
	

# Prints info about what the server is currently doing
def i(tag, event):
	log(Level.INFO, tag, event)

# Prints info that is to be used during testing only
def d(tag, event):
	log(Level.DEBUG, tag, event)

# Prints info about possible problems
def w(tag, event):
	log(Level.WARNING, tag, event)

# Prints info about definite problems
def e(tag, event):
	log(Level.ERROR, tag, event)

# same as map but with specific formatting
def get_json(json):
	return (get_mapf(json, BOLD + OKGREEN, ''))

# same as map but with specific formatting
def json(json):
	s_print(get_json(json))

# Takes a dict object(like json) and prints it out in a table
def get_map(map):
	box = []
	for key, value in map.items():
		box.append([key, value])

# Takes a dict object(like json) and prints it out in a table
def get_mapf(map, text_format, box_format):
	if not COLORED_LOG_MESSAGES:
		return get_map(map)
	b = []
	for key, value in map.items():
		b.append([key, value])
	return get_boxf(b, text_format, box_format)

# prints a dictionary in a table
def map(map):
	s_print(get_map(map))

# prints a dictionary in a table
def mapf(map, text_format, box_format):
	s_print(get_mapf(map, text_format, box_format))

# test area
def test():
	i("test info")
	d("test debug message")
	w("test warning")
	e("test error or failure")
	sock("test socket event")
	emit("test socket emit")
	box([
		['Author', 'Carsen Yates'],
		['Date created', '04/23/2017'],
		['Description', 'For making terminal\noutput look pretty']
	])
	boxf([
		['IM A BOX\n IMA BOX\n\n\n\n\n\n\n yur mum', 'One fish\ntwo fish\nred fish\nblueeeeeeeeeeeeeeeeeeeeeeeeee fish'],
		[get_mapf({
			'poops': 'farts',
			'dicks': 'buttholes',
			'boobs': 'vagina',
		}, UNDERLINE, CYAN), 'smoke weed all of the days'],
	], BOLD, MAGENTA)
	
