import unittest, worldgen

# Unit testing module for worldgen.py 

def print_grid_values(grid):
	return


class avgFnTestCase1(unittest.TestCase):
	def runTest(self):
		grid1 = worldgen.scale_grid(worldgen.white_noise(10,10),1)
		# print grid1
		grid2 = worldgen.scale_grid(worldgen.white_noise(5,5),2)
		# print grid2
		# print worldgen.avg_grids([grid2, grid1])

		assert(True)

if __name__ == '__main__':
	unittest.main()