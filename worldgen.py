import sys, random, math
import pathfinders

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

			# get the values at the four nearest corners in the original octave
			top_left = grid[int(math.floor(y_scale))][int(math.floor(x_scale))]
			top_right = grid[int(math.floor(y_scale))][int(math.ceil(x_scale))]
			bottom_left = grid[int(math.ceil(y_scale))][int(math.floor(x_scale))]
			bottom_right = grid[int(math.ceil(y_scale))][int(math.ceil(x_scale))]

			# interpolate top left to top right, then bottom left to bottom right, then interpolate those two
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

# retrieve value at point from a 2d array
def grid_at(grid, point):
	return grid[point[1]][point[0]]

# diamond square algorithm
def diamond_square(w,h):
	grid = [[0 for x in range(w)] for y in range(h)]
	grid_rect = ((0,0),(w-1,0),(0,h-1),(w-1,h-1))
	for point in grid_rect:
		grid[point[1]][point[0]] = random.random()

	rectangles = [grid_rect]
	# in general, a rectangle is (0,1,2,3), where:
	# 0----1
	# |    |
	# 2----3

	while rectangles:
		rect = rectangles.pop(0)
		# midpoint formula is equivalent to: 
		# with a rectangle (t1,t2,b1,b2): midpoint = ((t2.x-t1.x)/2),((b1.y-t1.y)/2)
		midpoint = (((rect[1][0]-rect[0][0])//2),((rect[2][1]-rect[1][1])//2))
		grid[midpoint[1]][midpoint[0]] = sum([grid_at(point) for point in rect])/len(rect) + random.uniform(-0.1,0.1)

		# generate the four rectangles
		if midpoint[0]-rect[0][0] >= 2 and midpoint[1]-rect[0][1] >= 2: # x at least 1 apart
			rectangles.append((rect[0],(midpoint[0],rect[0][1]),(rect[0][0],midpoint[0]),midpoint))
			rectangles.append(((midpoint[0],[rect[1][1]]),rect[1],midpoint,(rect[1][0],midpoint[1])))
			rectangles.append(((rect[2][0],midpoint[1]),midpoint,rect[2],(midpoint[0],rect[2][1])))
			rectangles.append((midpoint, (rect[3][0],midpoint[1]), (midpoint[0],rect[3][1]), rect[3]))

	return grid


# converts a 2d grid into their corresponding terrain type
def apply_thresholds(grid, terrain_composition=[(' ',0.6),('.',0.3),('^',0.1)]):
	grid_width = len(grid[0])
	grid_height = len(grid)

	actual_terrain_composition = {
		' ':0.0,
		'.':0.0,
		'^':0.0
	}
	ret = [[' ' for x in range(grid_width)] for y in range(grid_height)]
	flat_grid = zip([(x,y) for x in range(grid_width) for y in range(grid_height)],sum(grid, []))
	sorted_flat_grid = sorted(flat_grid, key=(lambda pair: pair[1]))

	for comp in terrain_composition:
		if debug_mode: 
			print comp
			print actual_terrain_composition[comp[0]]
		num_tiles_terrain = 0
		while abs(comp[1] - actual_terrain_composition[comp[0]]) > 0.01:
			if not sorted_flat_grid:
				break
			(coord, tile) = sorted_flat_grid.pop(0)
			ret[coord[1]][coord[0]] = comp[0]
			num_tiles_terrain += 1
			actual_terrain_composition[comp[0]] = float(num_tiles_terrain)/(grid_width*grid_height)
	else:
		while sorted_flat_grid:
			(coord, tile) = sorted_flat_grid.pop(0)
			ret[coord[1]][coord[0]] = terrain_composition[-1][0]

	'''
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


	# determine the data mean and std.dev, then use that to set the range
	avg = sum([sum(row) for row in grid])/(grid_width*grid_height)
	variance = sum([(tile-avg)**2 for tile in row for row in grid])/(grid_width*grid_height)
	stdev = variance**0.5

	terrain = [(avg-(0.2*stdev), ' '), (avg+(1.5*stdev), '.'), (1.1, '^')]


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
	'''
	return ret

# find_river: a quick greedy method to generate rivers by finding the lowest neighbor until a water tile is reached.
def find_river(height_map, world, start):
	current = start
	river = [start]
	width = len(world[0])
	height = len(world)

	while world[current[1]][current[0]] != ' ' and world[current[1]][current[0]] != '~':
		if debug_mode: print current
		adjacent_coords = [(current[0]-1,current[1]),(current[0]+1,current[1]),(current[0],current[1]-1),(current[0],current[1]+1)]
		if debug_mode: print adjacent_coords
		adjacent_coords = filter((lambda coord: coord not in river and coord[0] >= 0 and coord[1] >= 0 and coord[0] < width and coord[1] < height), adjacent_coords)
		if debug_mode: print adjacent_coords
		neighbors = [(world[coord[1]][coord[0]], coord) for coord in adjacent_coords] #
		if not neighbors:
			break
		current = min(neighbors)[1] # take the coordinate of the minimum neighbor
		river.append(current)

	if debug_mode: print river
	return river

# identify all the separate landmasses in a world using floodfill, returning it as a list of continents
# each continent is a list of coordinates
def identify_landmasses(world):
	landmasses = []

	world_map = world_map[:] # make a copy of the world for floodfill purposes

	width = len(world_map[0])
	height = len(world_map)

	for y in range(height):
		for x in range(width):
			if world_map[y][x] == ' ':
				continue

		tile_queue = [(x,y)] # evaluate tiles as a queue
		visited = []
		landmass = []

		while(tile_queue):
			current = tile_queue.pop(0)
			visited.append(current)
			if world_map[current[1]][current[0]] != ' ':
				adjacent_coords = [(current[0]-1,current[1]),(current[0]+1,current[1]),(current[0],current[1]-1),(current[0],current[1]+1)]
				if debug_mode: print adjacent_coords
				adjacent_coords = filter((lambda coord: coord not in visited and coord[0] >= 0 and coord[1] >= 0 and coord[0] < width and coord[1] < height), adjacent_coords)
				if debug_mode: print adjacent_coords
				tile_queue.extend(adjacent_coords)
				landmass.append(current)
				world_map[current[1]][current[0]] = ' '
		landmasses.push(landmass)

	return landmasses

# generate world: keeps generating worlds until a satisfactory one is found
def generate_world(w, h, terrain_composition=[(' ',0.3),('.',0.5),('^',0.2)], acceptable_margin=0.1):
	# terrain_composition is a list of tile to percentage tuples, eg. [(' ',0.3),('.',0.5),('^',0.2)]

	octaves = range(int(math.log(min(w,h),2)))[-5:] # takes the last 5 powers of 2 closest to min(w,h)
	if debug_mode: print 'octaves: ' + str(octaves)

	world_area = w*h
	worlds_generated = 0

	satisfactory_world = False # True if the world has the correct percentages of terrain
	while not satisfactory_world:
		noise_grid = generate_noise(w, h, octaves)
		world = apply_thresholds(noise_grid, terrain_composition)
		if debug_mode: print 'world #' + str(worlds_generated) + '\n' + prettify_grid(world)
		worlds_generated += 1 
		if debug_mode: print 'generated world #' + str(worlds_generated)
		satisfactory_world = True # satisfactory_world is set to true by default

		# checks for every tile if the actual composition is within an acceptable margin
		for (tile,proportion) in terrain_composition:
			tile_proportion = sum([row.count(tile) for row in world])/float(world_area)
			if debug_mode: print 'proportion of \'' + tile + '\' in world #' + str(worlds_generated) + ': ' + str(tile_proportion) + '(expected ' + str(proportion) + ')'
			if abs(tile_proportion - proportion) > acceptable_margin:
				satisfactory_world = False
				if debug_mode: print 'world #' + str(worlds_generated) + ' was rejected.'
				break

	if debug_mode: print 'world #' + str(worlds_generated) + ' passed!'
	# river_seed_grid = [[int(100.0*tile) for tile in row] for row in noise_grid]

	# generate rivers
	num_rivers = random.randint(octaves[0],octaves[-1])
	first_river = [] # store the first river
	for r in range(num_rivers):
		if debug_mode: print 'generating river %d of %d' % (r+1, num_rivers)

		# replace with better endpoint searching pls
		#p1 = (random.randint(0, ((w-1)//4)), random.randint(0, ((h-1)//4))) # generate random p1 from top-left quadrant
		#p2 = (random.randint((((w-1)*3)//4), (w-1)), random.randint((((h-1)*3)//4), (h-1))) # generate random p2 from bottom-right quadrant
		
		# remember, rivers flow from mountains to seas
		while True:
			p1 = (random.randint(0, ((w-1)//2)), random.randint(0, (h-1)))
			if world[p1[1]][p1[0]] == '^':
				break
		
		while True:
			p2 = (random.randint(((w-1)//2), (w-1)), random.randint(0, (h-1)))
			if world[p2[1]][p2[0]] == ' ':
				break

		'''
		if (first_river and random.random() > 0.5):
			p1 = random.choice(first_river) # pick p1 from first_river
		else:
			p1 = (random.randint(0, ((w-1)//4)), random.randint(0, (h-1)))
		p2 = (random.randint((((w-1)*3)//4), (w-1)), random.randint(0, (h-1)))
		'''

		#river_seed_grid = [[random.randint(1,15) for tile in row] for row in noise_grid]
		river_seed_grid = [[int(100.0*tile)+random.randint(-5,5) for tile in row] for row in noise_grid]
		#river = pathfinders.dijkstra(river_seed_grid, p1, p2)

		river = find_river(river_seed_grid, world, p1)
		#river = pathfinders.a_star(river_seed_grid, p1, p2, pathfinders.manhattan_distance)

		#river = pathfinders.greedy_best_first_search(river_seed_grid, p1, p2, pathfinders.manhattan_distance)
		for (y,x) in river:
			if world[y][x] == '^':
				break
			world[y][x] = '~' if world[y][x] == '.' else world[y][x]


		if (r < 2):
			first_river = river

		# generate structures

	return world

# prints a 2d array of characters without spaces between
def prettify_grid(grid):
	return '\n'.join([''.join(row) for row in grid])

def usage():
	print '''Usage: python worldgen.py [WIDTH] [HEIGHT] [options]
List of options:
	--debug - print debug messages
	--seed [SEED] - seed random number generator
	'''

if __name__ == "__main__":
	debug_mode = ('--debug' in sys.argv) # debug_mode is true if `--debug` is anywhere in the command

	if '--seed' in sys.argv:
		seed_input = int(sys.argv[sys.argv.index('--seed') + 1])
	else:
		seed_input = None
	
	random.seed(seed_input)

	if debug_mode: 
		print prettify_grid(generate_world(int(sys.argv[1]),int(sys.argv[2])))
		sys.exit()

	try:
		print prettify_grid(generate_world(int(sys.argv[1]),int(sys.argv[2])))

	except:
		usage()

		
