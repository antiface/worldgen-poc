import unittest, worldgen

# Unit testing module for worldgen.py 


class AvgFnTestCase1(unittest.TestCase):
	def runTest(self):
		grid1 = worldgen.scale_grid(worldgen.white_noise(10,10),1)
		print str(grid1).replace(']','\n').replace('[[','').replace(', [','')
		grid2 = worldgen.scale_grid(worldgen.white_noise(5,5),2)
		print str(grid2).replace(']','\n').replace('[[','').replace(', [','')

		print str(worldgen.avg_grids([grid2, grid1])).replace(']',',').replace('[[','').replace(', [','')

		# not really a test case, it just prints out the data so I can use it to run external tests
		assert(True)

class WorldGenTestCase1(unittest.TestCase):
	def runTest(self):
		worldgen.generate_world(64, 64, [(' ',0.3),('.',0.5),('^',0.2)])

		# assert that the map has 

		assert(True)

if __name__ == '__main__':
	unittest.main()