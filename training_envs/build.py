from distutils.dir_util import copy_tree
import json
import os

import cffi
import pathlib
import os


def build_env(name="env0", track_id=0, track_width=630, track_height=630, turn_range=6, speed_range=10, car_size_x=23, car_size_y=10):
    ffi = cffi.FFI()
    working_env_dir = f"training_envs/gymenvs/{name}"
    copy_tree("training_envs/base", working_env_dir)

    env_config = {
        "track_id": track_id,
        "track_height": track_height,
        "track_width": track_width,
        "car_size_x": car_size_x,
        "car_size_y": car_size_y,
    }

    with open(f"training_envs/configs/{name}.json", "w") as fp:
        json.dump(env_config, fp)
    
    with open(os.path.join(working_env_dir, "playground.h"), "r") as fp:
        playground_header = fp.read()
    
    playground_header = playground_header.replace("REPLACE_TRACK_WIDTH", str(track_width)) \
        .replace("REPLACE_TRACK_HEIGHT", str(track_height)) \
        .replace("REPLACE_MAX_TURN", str(turn_range)) \
        .replace("REPLACE_MAX_SPEED", str(speed_range)) \
        .replace("REPLACE_CAR_SIZE_X", str(car_size_x)) \
        .replace("REPLACE_CAR_SIZE_Y", str(car_size_y))

    with open(os.path.join(working_env_dir, "playground.h"), "w") as fp:
        fp.write(playground_header)
    
    h_file_name = os.path.join(working_env_dir, "playground.h")
    with open(h_file_name) as h_file:
        ffi.cdef(h_file.read())

    ffi.set_source(
        "race_env",
        '#include "playground.h"',
        sources=["playground.c"],
        extra_compile_args=["-w"],
    )
    ffi.compile(tmpdir=working_env_dir)
    
    with open(os.path.join(working_env_dir, "gymenv.py"), "r") as fp:
        gymenv_source = fp.read()
    
    gymenv_source = gymenv_source.replace("GYMENVCONFIG", name)

    with open(os.path.join(working_env_dir, "gymenv.py"), "w") as fp:
        fp.write(gymenv_source)
    