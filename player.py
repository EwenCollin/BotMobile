import numpy as np
import gym
from gym.wrappers import Monitor
from stable_baselines3 import DQN, DDPG, PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.vec_env import SubprocVecEnv

import time

from training.race_env_2.gymenv import Env
from training.race_env_1.gymenv import Env as TestEnv

dumEnv = Env(True, max_step=100000)
loadEnv = TestEnv(True, max_step=100000)

BOT = True



env = loadEnv

if BOT:
    model = PPO.load("race_ppo_models/model20", env=dumEnv)

while True:
    done = False
    obs = env.reset()
    for i in range(100000):
        # Predict
        if BOT:
            action, _states = model.predict(obs, deterministic=True)
        else:
            action = env.sample_action()
        # Get reward
        obs, reward, done, info = env.step(action)
        # Render
        env.render()

        #time.sleep(0.001)
        
        if done:
            break
env.close()