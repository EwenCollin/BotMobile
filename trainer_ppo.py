import numpy as np
import gym
from gym.wrappers import Monitor
from stable_baselines3 import DQN, DDPG, PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.vec_env import SubprocVecEnv

from training.race_env_2.gymenv import Env
from training.race_env_1.gymenv import Env as TestEnv

from utils import linear_schedule

dumEnv = Env(True, max_step=100000)
loadEnv = Env(True, max_step=100000)

TRAIN = True
TRAIN_RELOAD = True

if __name__ == '__main__':
    n_cpu = 6
    batch_size = 64
    env = make_vec_env(Env, n_envs=n_cpu, vec_env_cls=SubprocVecEnv)
    if TRAIN_RELOAD:
        model = PPO.load("race_ppo_models/model_renv0", env=env, custom_objects={"learning_rate": 1e-5})
    elif TRAIN:
        model = PPO("MlpPolicy",
                env,
                policy_kwargs=dict(net_arch=[dict(pi=[256, 256], vf=[256, 256])]),
                n_steps=batch_size * 12 // n_cpu,
                batch_size=batch_size,
                n_epochs=10,
                learning_rate=5e-5,#7e-6,#linear_schedule(7e-5),#7E-6
                gamma=0.99,
                verbose=2,
                tensorboard_log="race_ppo_logs/")
    # Train the model
    if TRAIN:
        for i in range(1):
            print("Training...")
            model.learn(total_timesteps=int(60e5))
            model.save("race_ppo_models/model_renv1")
            try:
                for i in range(2):
                    done = False
                    obs = dumEnv.reset()
                    for i in range(100000):
                        # Predict
                        action, _states = model.predict(obs, deterministic=True)
                        # Get reward
                        obs, reward, done, info = dumEnv.step(action)
                        # Render
                        dumEnv.render()
                        if done:
                            break
            except:
                print("Stopping display...")
        del model

    # Run the algorithm
    model = PPO.load("race_ppo_models/model_renv1", env=dumEnv)
    print("Starting test...")
    env = dumEnv
    #env = Monitor(env, directory="racetrack_ppo/videos", video_callable=lambda e: True)
    #env.unwrapped.set_monitor(env)

    while True:
        done = False
        obs = env.reset()
        for i in range(100000):
            # Predict
            action, _states = model.predict(obs, deterministic=True)
            # Get reward
            obs, reward, done, info = env.step(action)
            # Render
            env.render()
            if done:
                break
    env.close()