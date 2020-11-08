from gym_photosynthisis.envs.photosynthisis_env import PhotosynthisisEnv

print("Let's Play Photosynthisis!")

game = PhotosynthisisEnv()

game.step(None)

game.reset()

game.step(None)

print("Good Game!")
