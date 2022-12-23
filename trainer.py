from training_envs.build import build_env
import datetime
import os
import json
import glob

import importlib

from utils import linear_schedule

from stable_baselines3 import PPO, SAC
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.vec_env import SubprocVecEnv


MODEL = PPO

DONE_TRAININGS_DIR = "done_trainings"

MODELS_DIR = "race_models"



def create_env(data):
    env_data = data["TrainingEnv"]
    build_env(env_data["name"], env_data["track_id"],
        env_data["track_width"], env_data["track_height"],
        env_data["turn_range"], env_data["speed_range"],
        env_data["car_size_x"], env_data["car_size_y"],
        env_data["other_car_nb"], env_data["other_car_history"],
        env_data["records_dirname"], env_data["max_steps_count"],
        env_data["use_records"])

def on_training_done(data, schedule_filename):
    with open(os.path.join(DONE_TRAININGS_DIR, schedule_filename), "w") as fp:
        now = datetime.datetime.now()
        info = {"EndTime": now.strftime("%Y-%m-%d %H:%M:%S")}
        json.dump(info, fp)

def train(data):
    n_cpu = 6
    batch_size = 64
    Env = getattr(importlib.import_module(f'training_envs.gymenvs.{data["TrainingEnv"]["name"]}.gymenv'), "Env")
    env = make_vec_env(Env, n_envs=n_cpu, vec_env_cls=SubprocVecEnv)
    load_from = data["load"]
    if data["FixedLearningRate"]:
        learning_rate = data["LearningRate"]
    else:
        learning_rate = linear_schedule(data["LearningRate"])
    if len(load_from) > 0:
        model = MODEL.load(os.path.join(MODELS_DIR, load_from), env=env, custom_objects={"learning_rate": learning_rate})
    else:
        
        model = MODEL("MlpPolicy",
                env,
                policy_kwargs=dict(net_arch=[dict(pi=[256, 256], vf=[256, 256])]),
                n_steps=batch_size * 12 // n_cpu,
                batch_size=batch_size,
                n_epochs=10,
                learning_rate=learning_rate,#7e-6,#linear_schedule(7e-5),#7E-6#5E-5
                gamma=0.99,
                verbose=2,
                tensorboard_log="race_logs/")
        
        """
        model = MODEL("MlpPolicy",
                env,
                #policy_kwargs=dict(net_arch=[dict(pi=[256, 256], vf=[256, 256])]),
                #n_steps=batch_size * 12 // n_cpu,
                #batch_size=batch_size,
                #n_epochs=10,
                #learning_rate=learning_rate,#7e-6,#linear_schedule(7e-5),#7E-6#5E-5
                #gamma=0.99,
                verbose=2,
                tensorboard_log="race_logs/")
        """
    model.learn(data["steps"])
    model.save(os.path.join(MODELS_DIR, data["save"]))


def main_loop():
    while True:
        schedules = sorted(glob.glob("schedule/*.json"))
        schedule_filenames = [os.path.basename(schedule) for schedule in schedules]
        done_trainings = glob.glob(DONE_TRAININGS_DIR + "/*.json")
        done_trainings_filenames = [os.path.basename(training) for training in done_trainings]

        next_training_id = -1
        for i, schedule_filename in enumerate(schedule_filenames):
            if schedule_filename not in done_trainings_filenames:
                next_training_id = i
                break
        
        if next_training_id >= 0:
            training_session = schedules[next_training_id]

            
            with open(training_session, "r") as fp:
                session_data = json.load(fp)

            
            print(f'Training {training_session} - {session_data["DisplayName"]}')
            
            try:
                create_env(session_data)
            except:
                print("Error creating env :", json.dumps(session_data))
            
            try:
                train(session_data)
            except:
                print("Error while training :", json.dumps(session_data))
            
            try:
                on_training_done(session_data, schedule_filenames[next_training_id])
            except:
                print("Error after training :", json.dumps(session_data), training_session)


if __name__ == "__main__":
    main_loop()

