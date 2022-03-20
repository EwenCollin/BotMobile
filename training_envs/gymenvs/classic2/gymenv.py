import cffi
from .race_env import lib as cpenv

import os
import pathlib
pathlib.Path(__file__).parent.resolve()

import json

import math
import numpy as np
import gym
from gym import spaces

from typing import Optional, Union


from env_display.display import Renderer

import pygame

from random import randint

from random import random

from PIL import Image

ffi = cffi.FFI()



class Env(gym.Env):

    ACTION_NUMBER = 4

    WIDTH = 630
    HEIGHT = 630

    DWIDTH = 2000
    DHEIGHT = 2000

    DISPLAY_WIDTH = 630
    DISPLAY_HEIGHT = 630

    DISTANCE_RESOLUTION = 70
    BASE_GRID_X = 9
    BASE_GRID_Y = 9

    CAR_SIZE_X = 23
    CAR_SIZE_Y = 10

    STATE_SIZE = 6
    STATE_HISTORY = 1
    SELF_HISTORY = 1
    SELF_HISTORY_MOD = 10

    RAY_NB = 17

    MAX_ACCELERATION = 10#10*5
    MAX_TURNING = 10#10*5

    MAX_STEPS_COUNT = 15000#10000


    CURRENT_ENV_ID = 4

    metadata = {"render.modes": ["human"], "video.frames_per_second": 60}


    def __init__(self, init_all=True, max_step=15000):
        
        self.load_config()

        self.MAX_STEPS_COUNT = max_step
        
        self.ANGLES = [(i/(self.RAY_NB-1))*math.pi/2 - math.pi/4 for i in range(self.RAY_NB)]
        self.STATE_SIZE = len(self.ANGLES) + 2

        pygame.init()
        pygame.font.init()

        #self.action_space = spaces.Discrete(self.ACTION_NUMBER)
        action_low = [-1, -1]
        action_high = [1, 1]
        self.action_space = spaces.Box(np.array(action_low, dtype=np.float32), np.array(action_high, dtype=np.float32), dtype=np.float32)

        max_scan_distance = math.sqrt(self.DWIDTH*self.DWIDTH + self.DHEIGHT*self.DHEIGHT)

        state_high = [max_scan_distance for i in self.ANGLES] + [10, 10]
        state_low = [0 for i in self.ANGLES] + [-10, -10]

        high = np.array([
                state_high[j%len(state_high)] for j in range(self.STATE_SIZE*self.SELF_HISTORY)
        ], dtype=np.float32)
        low = np.array([
                state_low[j%len(state_high)] for j in range(self.STATE_SIZE*self.SELF_HISTORY)
        ], dtype=np.float32)

        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        print(high)
        print(self.observation_space)

        reward_range = (-100, 1)

        #DISPLAY
        self.screen = None
        self.isopen = False
        #self.renderer = Renderer(self.WIDTH, self.HEIGHT, self.CAR_SIZE_X, self.CAR_SIZE_Y, self.get_background_filename())
        
        self.track_data = {}
        self.bots_current = []
        self.load_track_data()

        if init_all:
            filename_char = ffi.new("char[]", self.get_track_filename().encode())
            cpenv.load_terrain_file(filename_char)
            cpenv.set_lid_ray_nb(self.RAY_NB)
            ray_array = ffi.new("float[]", self.ANGLES)
            cpenv.set_lid_rays(ray_array)
            #init()

        im = Image.open(self.get_spawn_filename())
        self.spawn_pix = im.convert("RGB")
        
        self.previous_states = [0 for i in range(self.STATE_SIZE*self.SELF_HISTORY)]
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.rotation = 0.0
        self.speed = 0.0
        self.direction = 0.0
        self.step_count = 0
        self.done_status = 0
        self.dist_save_a = 0
        self.dist_save_b = 0
    
    def load_config(self):
        with open(os.path.join(pathlib.Path().resolve(), f"training_envs/configs/classic2.json"), "r") as fp:
            config_data = json.load(fp)
            self.CURRENT_ENV_ID = config_data["track_id"]
            self.CAR_SIZE_X = config_data["car_size_x"]
            self.CAR_SIZE_Y = config_data["car_size_y"]
            self.WIDTH = config_data["track_width"]
            self.HEIGHT = config_data["track_height"]

    
    def get_background_filename(self):
        return os.path.join(pathlib.Path().resolve(), "race_tracks/raw_tracks", str(self.CURRENT_ENV_ID) + ".png")

    def get_track_filename(self):
        return os.path.join(pathlib.Path().resolve(), "race_tracks/ready_tracks", str(self.CURRENT_ENV_ID) + ".track")
    
    def load_track_data(self):
        with open(os.path.join(pathlib.Path().resolve(), f"race_tracks/track_data/{self.CURRENT_ENV_ID}.json"), "r") as fp:
            self.track_data = json.load(fp)
    
    def get_spawn_filename(self):
        return os.path.join(pathlib.Path().resolve(), "race_tracks/track_spawn", str(self.CURRENT_ENV_ID) + ".png")

    def get_cast_points(self):
        return [[cpenv.cast_ray_x(float(self.pos_x), float(self.pos_y), float(angle + self.rotation)), cpenv.cast_ray_y(float(self.pos_x), float(self.pos_y), float(angle + self.rotation))] for angle in self.ANGLES]

    def get_current_distance(self):
        return cpenv.get_distance_at(float(self.pos_x), float(self.pos_y))
    
    def collect_step_data(self):
        self.done_status = cpenv.get_done_status()
        self.pos_x = cpenv.get_position_x()
        self.pos_y = cpenv.get_position_y()
        self.rotation = cpenv.get_rotation()
        self.speed = cpenv.get_speed()
        self.direction = cpenv.get_direction()
        self.step_count = cpenv.get_step_count()
        self.dist_save_a = cpenv.get_dist_save_a()
        self.dist_save_b = cpenv.get_dist_save_b()
    
    def set_step_data(self):
        cpenv.set_step_data(float(self.pos_x), float(self.pos_y), float(self.rotation), float(self.speed), float(self.direction), int(self.step_count), int(self.done_status), int(self.dist_save_a), int(self.dist_save_b))
    
    def get_state(self, collect_data=True):
        if collect_data:
            self.collect_step_data()
        states = cpenv.get_state()
        for i in range(self.STATE_SIZE*self.SELF_HISTORY):
            if i >= self.STATE_SIZE*(self.SELF_HISTORY - 1):
                self.previous_states[i] = states[int(i - self.STATE_SIZE*(self.SELF_HISTORY - 1))]
            elif self.step_count % self.SELF_HISTORY_MOD == 0:
                self.previous_states[i] = self.previous_states[i+self.STATE_SIZE]
        return np.array(self.previous_states, dtype=np.float32)

    def reset_state_data(self):
        self.previous_states = [0 for i in range(self.STATE_SIZE*self.SELF_HISTORY)]
        """
        RANDOM POS (NEW)
        """
        self.pos_x = randint(0, self.WIDTH - 1)
        self.pos_y = randint(0, self.HEIGHT - 1)

        while self.spawn_pix.getpixel((self.pos_x, self.pos_y))[0] != 0:
            self.pos_x = randint(0, self.WIDTH - 1)
            self.pos_y = randint(0, self.HEIGHT - 1)


        #self.pos_x = self.track_data["starts"][0]["x"]
        #self.pos_y = self.track_data["starts"][0]["y"]
        #self.rotation = self.track_data["starts"][0]["rot"]
        self.rotation = random()*2*math.pi
        self.speed = 0.0
        self.direction = 0.0
        self.step_count = 0
        self.done_status = 0
        self.dist_save_a = 0
        self.dist_save_b = 0

    def reset(self,*,
        seed: Optional[int] = None,
        return_info: bool = False,
        options: Optional[dict] = None,):
        self.reset_state_data()
        cpenv.reset()
        return self.get_state(collect_data=False)
    
    def step(self, action, dt=1/60, convert_action=False):#dt=1/5, convert_action=True):
        self.set_step_data()

        cpenv.reset_collision_points()

        for bot in self.bots_current:
            cpenv.add_car_collision_points(float(bot[0]), float(bot[1]), float(bot[2]))

        #DISCRETE FOR DQN
        if convert_action:
            act = [0, 0]
            if action == 0:
                act[0] = 1
            elif action == 1:
                act[0] = - 1
            elif action == 2:
                act[1] = 1
            elif action == 3:
                act[1] = - 1
        else:
            act = action

        rwd = cpenv.step(float(act[0]*self.MAX_ACCELERATION), float(act[1]*self.MAX_TURNING), float(dt))
        #rwd = step(float(self.MAX_ACCELERATION*action[0]), float(self.MAX_TURNING*action[1]), float(dt))
        done = cpenv.get_done_status() == 1
        state = self.get_state()
        if self.step_count >= self.MAX_STEPS_COUNT:
            return state, -5000, True, {}#return state, -200, True, {}
        return state, rwd if not done else -3000, done, {}#return state, (rwd + 1)/2 if not done else -100, done, {}
    
    def pos_rot(self):
        return self.pos_x, self.pos_y, self.rotation
    
    def set_bots_current(self, bot_data):
        self.bots_current = bot_data
    
    def sample_action(self):
        keys = pygame.key.get_pressed()
        action = [int(keys[pygame.K_UP]) - int(keys[pygame.K_DOWN]), int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])]
        
        return action

    def render(self, mode="human", draw_info=0, debug=False):
        if self.screen is None:
            #pygame.init()
            #pygame.font.init()
            self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
            self.screen_font = pygame.font.SysFont('Arial', 22)
            self.renderer = Renderer(self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT, self.CAR_SIZE_X, self.CAR_SIZE_Y, self.WIDTH, self.HEIGHT, self.get_background_filename())
            self.isopen = True
        self.renderer.render_reset(self.screen)

        psx, psy, rtn = self.pos_rot()
        self.renderer.render_background(self.screen, psx, psy)

        for bot in self.bots_current:
            self.renderer.render_car(self.screen, psx, psy, bot[0], bot[1], bot[2], False)

        self.renderer.render_car(self.screen, psx, psy, psx, psy, rtn, True)
        #for point in self.get_cast_points():
        #    pygame.draw.line(self.screen, (255, 0, 0), [int(psx), int(psy)], [int(point[0]), int(point[1])])

        
        if mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
            )
        else:
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pass
                    #running = False
                    #py.quit()
            return self.isopen
    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.isopen = False

