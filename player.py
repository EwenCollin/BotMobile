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

from training_envs.gymenvs.unit2.gymenv import Env as Classic

dumEnv = Env(True, max_step=100000)
loadEnv = TestEnv(True, max_step=100000)

BOT = True



env = Classic(True, max_step=3000)

if BOT:
    model = PPO.load("race_models/model_unit3", env=env)

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
        #print(obs)
        # Render
        env.render()

        time.sleep(0.02)
        
        if done:
            break
env.close()