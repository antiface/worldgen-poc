import sys, random, math

# worldgen

# check if two floats are equal
def float_equal(a,b):
	return abs(a-b) <= 0.0000001

# generates a wxh 2d array of white noise (floats between 0 and 1)
def white_noise(w,h):
	w = int(w)
	h = int(h)
	return [[random.random() for i in range(0,w)] for j in range(0,h)]

# cosine interpolate a <= x <= b, interpolates x on a stretched cosine curve between a and b
def cosine_interpolate(a,b,x):
	f=1-math.cos(0.5*math.pi*x)
	return (a*(f)+b*(1-f))

# linear interpolate a <= x <= b, interpolates x on a straight line between a and b
def linear_interpolate(a,b,c):
	f = x
	return (a*(f)+b*(1-f))

# scales up a grid and interpolates
# in other words, it creates the kth octave where (using default settings) k=|8-factor|.
def generate_octave(grid, factor):
	factor = 2.0**factor
	if factor == 1:
		return grid	

	grid_height = len(grid)
	new_height = int(factor*grid_height)

	grid_width = len(grid[0])
	new_width = int(factor*grid_width)

	ret = []

	for y in range(new_height):
		y_scale = (float(y)/new_height)*(grid_height-1)

		row = []
		for x in range(new_width):
			x_scale = (float(x)/new_width)*(grid_width-1)

			top_left = grid[int(math.floor(y_scale))][int(math.floor(x_scale))]
			top_right = grid[int(math.floor(y_scale))][int(math.ceil(x_scale))]
			bottom_left = grid[int(math.ceil(y_scale))][int(math.floor(x_scale))]
			bottom_right = grid[int(math.ceil(y_scale))][int(math.ceil(x_scale))]

			blend_top = cosine_interpolate(top_left, top_right, x_scale-math.floor(x_scale))
			blend_bottom = cosine_interpolate(bottom_left, bottom_right, x_scale-math.floor(x_scale))
			blend_overall = cosine_interpolate(blend_top, blend_bottom, y_scale-math.floor(y_scale))

			row.append(blend_overall)
		ret.append(row)

	return ret

	

# averages all grids in the array
def avg_grids(grids):
	amplitude = 0.5
	total_amplitude = 0
	persistence = 0.5
	height = len(grids[0])
	width = len(grids[0][0])

	final_grid = [[0 for i in range(width)] for j in range(height)]

	# add up the weighted values of all the octaves
	for grid in grids:
		for y in range(len(grid)):
			for x in range(len(grid[y])):
				final_grid[y][x] += grid[y][x] * amplitude

		total_amplitude += amplitude
		amplitude *= persistence

	# normalize the final graph
	'''
	for y in range(0, len(grid)):
					for x in range(0, len(grid[y])):
						final_grid[y][x] /= total_amplitude
	'''

	return final_grid

# generates noise grid by generating and summing up octaves
# the default octave scales are 
def generate_noise(w, h, octaves=range(3,9)[::-1]):
	return avg_grids([generate_octave(white_noise(w*(2**(octave-octaves[0])), h*(2**(octave-octaves[0]))), (octaves[0]-octave)) for octave in octaves])

# converts a 2d grid into their corresponding terrain type
def threshold_noise_to_terrain(grid, 
	thresholds={ 
		(0.0,0.2): '.',
		(0.2,0.5): '_',
		(0.5,1.0): '^'
	}):

	print grid

	ret = []
	for row in grid:
		ret_row = []
		for point in row:
			# check thresholds for grid

			if point < 0.45:
				char = ' '
			elif point < 0.65:
				char = '.'
			else:
				char = '^'

			ret_row.append(char)
		ret.append(ret_row)
	return ret

# prints a 2d array of characters without spaces between
def prettify_grid(grid):
	return '\n'.join([''.join(row) for row in grid])

def usage():
	print 'Usage: python worldgen.py [WIDTH] [HEIGHT]'

if __name__ == "__main__":
	try:

		noise_grid = generate_noise(int(sys.argv[1]),int(sys.argv[2]))
		print prettify_grid(threshold_noise_to_terrain(noise_grid))
	except:
		usage()
