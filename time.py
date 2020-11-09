import timeit

mysetup = """
from photosynthisis_env import PhotosynthisisEnv
game = PhotosynthisisEnv()
"""

mycode = """
game.reset()
game.step(None)
"""

iterations = 10000

print(timeit.timeit(setup = mysetup,
                    stmt = mycode,
                    number = iterations)/iterations)
