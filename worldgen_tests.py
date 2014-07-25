import unittest, worldgen

# Unit testing module for worldgen.py 


class AvgFnTestCase1(unittest.TestCase):
	def runTest(self):
		grid1 = worldgen.scale_grid(worldgen.white_noise(10,10),1)
		print str(grid1).replace(']','\n').replace('[[','').replace(', [','')
		grid2 = worldgen.scale_grid(worldgen.white_noise(5,5),2)
		print str(grid2).replace(']','\n').replace('[[','').replace(', [','')
		print str(worldgen.avg_grids([grid2, grid1])).replace(']',',').replace('[[','').replace(', [','')
		assert(True)

'''
class WorldGenTestCase1(unittest.TestCase):
	def runTest(self):
		noise_grids = worldgen.generate_noise(128,128)
		print noise_grids
		print ''
		print worldgen.prettify_grid(worldgen.threshold_noise_to_terrain(noise_grids))
		assert(True)
'''

if __name__ == '__main__':
	unittest.main()