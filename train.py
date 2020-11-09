import gym
import numpy as np
import matplotlib.pyplot as plt

from photosynthisis_env import PhotosynthisisEnv

# from stable_baselines.deepq import MlpPolicy
from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from stable_baselines import results_plotter
from stable_baselines.bench import Monitor

from stable_baselines.results_plotter import load_results, ts2xy
from stable_baselines.common.noise import AdaptiveParamNoiseSpec, NormalActionNoise
from stable_baselines.common.callbacks import BaseCallback

import os, sys
import time
import logz

def moving_average(values, window):
    """
    Smooth values by doing a moving average
    :param values: (numpy array)
    :param window: (int)
    :return: (numpy array)
    """
    weights = np.repeat(1.0, window) / window
    return np.convolve(values, weights, 'valid')


def plot_results(log_folder, title='Learning Curve PPO2'):
    """
    plot the results

    :param log_folder: (str) the save location of the results to plot
    :param title: (str) the title of the task to plot
    """
    x, y = ts2xy(load_results(log_folder), 'timesteps')

    y = moving_average(y, window=100)
    # Truncate x
    x = x[len(x) - len(y):]

    fig = plt.figure(title)
    plt.plot(x, y)
    plt.xlabel('Number of Timesteps')
    plt.ylabel('Rewards')
    plt.title(title + " Smoothed")
    plt.show()


if not(os.path.exists('data')):
    os.makedirs('data')
if not(os.path.exists('game_logs')):
    os.makedirs('game_logs')
logdir = 'photosynthisis_PPO2_-v0_' + time.strftime("%d-%m-%Y_%H-%M-%S")
logdir = os.path.join('data', logdir)
if not(os.path.exists(logdir)):
    os.makedirs(logdir)

env = PhotosynthisisEnv(prespecified_players=[PhotosynthisisEnv.ai,None,None,None])
env = Monitor(env, logdir)

model = PPO2(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=10000000, log_interval=1000)
model.save("models/PPO2_models/photosynthisis_PPO2_model_v1")

print(env.record)

plot_results(logdir)
