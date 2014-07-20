# worldgen-poc
### by [Elvin Yung](https://github.com/elvinyung)

## Description
Proof-of-concept 2d terrain generation, for a game I'm working on. The core of the generator involves a Perlin noise function over a 2d grid, using cosine interepolation to achieve smoother values, although linear interpolation is also implemented. After that, multiple threshold functions are applied to determine terrain features.

## Usage:
`python worldgen.py [WIDTH] [HEIGHT]`