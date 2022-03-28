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

from training_envs.gymenvs.fwdoptm0.gymenv import Env as Classic

dumEnv = Env(True, max_step=100000)
loadEnv = TestEnv(True, max_step=100000)

BOT = False

RECORDS = []

def load_records(path, nb):
    for i in range(nb):
        with open(f"{path}/{i}.record", "r") as fp:
            rec = fp.read()
            RECORDS.append([float(x) for x in rec.split(",") if len(x) > 0])


load_records("race_records/6/fwdoptrec0", 3)


env = Classic(init_all=False, max_step=3500)

if BOT:
    model = PPO.load("race_models/model_fwdopt3", env=env)

while True:
    done = False
    obs = env.reset()
    for i in range(100000):
        # Predict
        if BOT:
            action, _states = model.predict(obs, deterministic=False)
        else:
            action = env.sample_action()
        # Get reward
        obs, reward, done, info = env.step(action)
        #print(obs)
        # Render
        env.set_bots_current([x[i*3:(i+1)*3] for x in RECORDS])
        env.render()

        time.sleep(0.05)
        
        if done:
            break
env.close()