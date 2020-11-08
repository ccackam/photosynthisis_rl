from gym_photosynthisis.envs.photosynthisis_env import PhotosynthisisEnv

from stable_baselines.common.env_checker import check_env

env = PhotosynthisisEnv()

check_env(env)
