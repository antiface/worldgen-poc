import sys, random, math

# worldgen

# HELPER FUNCTIONS

debug_mode = True

# float_equal check if two floats are equal
def float_equal(a,b):
	return abs(a-b) <= 0.0000001

# returns the euclidean distance between points p1 and p2
def point_distance(p1,p2):
	return math.sqrt(sum([(x-y)**2 for (x,y) in zip(p1,p2)]))

# NOISE GENERATION FUNCTIONS

# generates a wxh 2d array of white noise (floats between 0 and 1)
def white_noise(w,h, weight_points=[], proximity=5.0):
	w = int(w)
	h = int(h)
	grid = [[random.random() for i in range(w)] for j in range(h)]

	if weight_points:
		for y in range(h):
			for x in range(w):
				for pt in weight_points:
					if point_distance(pt, (x,y)) <= proximity:
						grid[y][x] += math.min(random.random(), 1.0-grid[y][x])


	#if debug_mode: print grid
	return grid

# THE ACTUAL ALGORITHM

# interpolate a <= x <= b, interpolates x on a stretched cosine curve between a and b
# default function is
def interpolate(a,b,x,f=(lambda x: math.cos(0.5*math.pi*x))):
	return (a*(f(x))+b*(1-f(x)))

# scales up a grid by factor of 2**factor rand interpolates
# in other words, it creates the kth octave where (using default settings) k=|8-factor|.
def scale_grid(grid, factor):
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

			blend_top = interpolate(top_left, top_right, x_scale-math.floor(x_scale))
			blend_bottom = interpolate(bottom_left, bottom_right, x_scale-math.floor(x_scale))
			blend_overall = interpolate(blend_top, blend_bottom, y_scale-math.floor(y_scale))

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
	for y in range(0, len(grid)):
					for x in range(0, len(grid[y])):
						final_grid[y][x] /= total_amplitude

	return final_grid

# generates noise grid by generating and summing up octaves
# the default octave scales are 
# needs rewrite, this is pretty hacky right now
def generate_noise(w, h, octaves=[4,5,6,7,8]):
	return avg_grids([scale_grid(white_noise(w*(2**(octave-octaves[-1])), h*(2**(octave-octaves[-1]))), 2**(octaves[-1]-octave)) for octave in octaves])

# POST-PROCESSING

# converts a 2d grid into their corresponding terrain type
# TODO: make the terrain dict dynamic to the data given
def apply_thresholds(grid):

	# analyze grid to determine terrain

	# determine the data mean and std.dev, then use that to set the range

	grid_width = len(grid[0])
	grid_height = len(grid)

	avg = sum([sum(row) for row in grid])/(grid_width*grid_height)
	variance = sum([(tile-avg)**2 for tile in row for row in grid])/(grid_width*grid_height)
	stdev = variance**0.5

	terrain = [(avg-(0.6*stdev), ' '), (avg+(1.25*stdev), '.'), (1.1, '^')]

	ret = []
	for row in grid:
		ret_row = []

		for height in row:

			# check thresholds for tile
			for (ubound, tile) in terrain:
				if height <= ubound:
					ret_row.append(tile)
					break
			
		ret.append(ret_row)
	return ret


# generate world: keeps generating worlds until a satisfactory one is found
def generate_world(w, h, terrain_composition, acceptable_margin=0.05):
	# terrain_composition is a list of tile to percentage tuples, eg. [(' ',0.3),('.',0.5),('^',0.2)]

	octaves = range(int(math.log(min(w,h),2)))[-5:] # takes the last 5 powers of 2 closest to min(w,h)
	if debug_mode: print 'octaves: ' + str(octaves)

	world_area = w*h
	worlds_generated = 0

	satisfactory_world = False # True if the world has the correct percentages of terrain
	while not satisfactory_world:
		world = apply_thresholds(generate_noise(w, h, octaves))
		if debug_mode: print 'world #' + str(worlds_generated) + '\n' + prettify_grid(world)
		worlds_generated += 1
		if debug_mode: print 'generated world #' + str(worlds_generated)
		satisfactory_world = True

		# checks for every tile if the actual composition is within an acceptable margin
		for (tile,proportion) in terrain_composition:
			tile_proportion = sum([row.count(tile) for row in world])/float(world_area)
			if debug_mode: print 'proportion of \'' + tile + '\' in world #' + str(worlds_generated) + ': ' + str(tile_proportion)
			if abs(tile_proportion - proportion) > acceptable_margin:
				satisfactory_world = False
				break

		if debug_mode and satisfactory_world: print 'world #' + str(worlds_generated) + ' passed!'

	return world

# prints a 2d array of characters without spaces between
def prettify_grid(grid):
	return '\n'.join([''.join(row) for row in grid])

def usage():
	print '''Usage: python worldgen.py [WIDTH] [HEIGHT] [options]
List of options:
	--debug - print debug messages
	'''

if __name__ == "__main__":
	try:
		debug_mode = ('--debug' in sys.argv)
		print prettify_grid(generate_world(int(sys.argv[1]),int(sys.argv[2]), [(' ',0.4),('.',0.5),('^',0.1)]))

	except:
		usage()

		
