import random

# check if two floats are equal
def float_equal(a,b):
	return abs(a-b) <= 0.0000001

# dot_product: takes two tuples v1 and v2, and returns its dot product  
def dot_product(v1, v2):
	try:
		return sum([v1[i]*v2[i] for i in range(len(v1))])
	except:
		raise Exception('error: v1 and v2 have different dimensions')

# generates a random vector (2d tuple) of given length
def random_vector(length):
	x = random.uniform(-1.0,1.0)
	y = (1.0-x ** 2.0) ** 0.5
	y *= -1 if random.random() > 0.5 else 1
	return (x,y)