
from numpy import record
from stable_baselines3 import DQN, DDPG, PPO
import os

import importlib

import time

import json

from trainer import create_env


def play_and_record(spawn, model, record_env, stop_step, other_history):
    print("PLAY & RECORD")
    spawn_x, spawn_y, spawn_rot = spawn
    

    done = True

    while done:
        obs = record_env.reset()
        record_env.pos_x = spawn_x
        record_env.pos_y = spawn_y
        record_env.rotation = spawn_rot

        history = []
        
        done = False
        for i in range(stop_step):
            action, _states = model.predict(obs, deterministic=False)
            record_env.reset_car_collision()
            for rec in other_history:
                record_env.add_car_collision_points(rec[i*3], rec[i*3+1], rec[i*3+2])
            obs, reward, done, info = record_env.step(action, reset_car_collisions=False)

            pos_x, pos_y, rot = record_env.pos_rot()

            history.append(pos_x)
            history.append(pos_y)
            history.append(rot)

            if done:
                break
    
    return history


def save_record(history, filename):
    history_str = ",".join([str(float(x)) for x  in history]) + ","

    with open(filename, "w") as fp:
        fp.write(history_str)



def record_all(model, env, record_config):
    stop_step = record_config["stop_step"]
    output_dir = record_config["output_dir"]
    env_id = record_config["env_id"]

    records = []
    for i, spawn in enumerate(record_config["spawns"]):
        current_history = play_and_record([spawn["x"], spawn["y"], spawn["rot"]], model, env, stop_step, records)
        records.append(current_history)
        os.makedirs(f"race_records/{env_id}/{output_dir}", exist_ok=True)
        save_record(current_history, os.path.join(f"race_records/{env_id}/{output_dir}", str(i) + ".record"))
    
def get_env(record_config):
    return getattr(importlib.import_module(f'training_envs.gymenvs.{record_config["record_env"]}.gymenv'), "Env")

def load_model(record_config, record_env):
    return PPO.load(f"race_models/{record_config['model_name']}", env=record_env)

def make_record(name):
    with open(f"record_configs/envs/{name}.json", "r") as fp:
        training_data = json.load(fp)
    
    create_env(training_data)
    print("Env created")

    with open(f"record_configs/records/{name}.json", "r") as fp:
        record_config = json.load(fp)
    
    record_env = get_env(record_config)
    env = record_env(init_all=False)
    print("Env loaded")
    record_model = load_model(record_config, env)
    print("Model loaded")


    print("Starting record")
    record_all(record_model, env, record_config)
    print("Done all records")


if __name__ == "__main__":
    make_record("02")