import math
import pygame as py


class Terrain:

    WALL_COLOR = (30, 30, 30)
    PATH_COLOR = (220, 220, 220)
    CHECK_COLOR = (255, 10, 10)

    DEBUG = False

    GRID_RES = 16

    def __init__(self, width, height, img_path_to_load=""):
        self.width = width
        self.height = height
        self.base_shape = [
            [1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,0,1,0,1],
            [1,0,1,0,0,0,1,0,1],
            [1,0,1,1,1,1,1,0,1],
            [1,0,1,1,1,0,0,0,1],
            [1,0,1,1,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1]
        ]
        self.base_dims = [len(self.base_shape), len(self.base_shape[0])]
        self.start_rotation = math.pi
        self.start_pos = [self.width/2, self.height/2]
        self.block_size = [self.width/self.base_dims[0], self.height/self.base_dims[1]]
        self.points = self.generate_shape()
        self.checked = []
        self.dist_shape = self.generate_dist_shape()
    
    def get_goal_pos(self):
        return [500, 300]
    
    def get_grid_scale(self):
        return self.block_size[0]/self.GRID_RES

    def get_grid_width(self):
        return self.base_dims[0]*self.GRID_RES
    
    def get_grid_height(self):
        return self.base_dims[0]*self.GRID_RES

    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_start_rotation(self):
        return self.start_rotation
    
    def draw(self, surface, distances=None, distances_width=0, distances_height=0):
        if distances is not None:
            for x in range(distances_width):
                for y in range(distances_height):
                    max_dist = 2000
                    intens = int(255*max(0, max_dist - distances[x*distances_width + y])/max_dist)
                    color = (intens, intens, intens)
                    size_x = self.width/distances_width
                    size_y = self.height/distances_height
                    py.draw.rect(surface, color, py.Rect(x*size_x, y*size_y, size_x, size_y))
        else:
            for x, line in enumerate(self.base_shape):
                for y, e in enumerate(line):
                    py.draw.rect(surface, self.WALL_COLOR if e == 0 else self.PATH_COLOR, py.Rect(x*self.block_size[0], y*self.block_size[1], self.block_size[0], self.block_size[1]))

            if self.DEBUG:
                for check in self.checked:
                    py.draw.rect(surface, self.CHECK_COLOR, py.Rect(check[0], check[1], 1, 1))
            self.checked = []
    
    def get_start_pos(self):
        return self.start_pos
    
    def is_wall(self, x, y):
        self.checked.append([x, y])
        return 0 <= x < self.width and 0 <= y < self.height and self.points[x][y] == 1

    def is_wall_grid(self, x, y):
        return 0 <= x < self.base_dims[0]*self.GRID_RES and 0 <= y < self.base_dims[1]*self.GRID_RES and self.dist_shape[x][y] == 1
    
    def generate_dist_shape(self):
        return [[ self.base_shape[int(x/self.GRID_RES)][int(y/self.GRID_RES)] for y in range(self.base_dims[1]*self.GRID_RES)] for x in range(self.base_dims[0]*self.GRID_RES)]

    def generate_shape(self):
        base_array = [[0 for y in range(self.height)] for x in range(self.width)]
        for i in range(self.base_dims[0]):
            for j in range(self.base_dims[1]):
                for x in range(math.ceil(self.block_size[0])):
                    for y in range(math.ceil(self.base_dims[1])):
                        if int(i*self.block_size[0] + x) < self.width and int(j*self.block_size[1] + y) < self.height:
                            base_array[int(i*self.block_size[0] + x)][int(j*self.block_size[1] + y)] = self.base_shape[i][j]
        return base_array
        return [[ self.base_shape[round(x/self.block_size[0])][round(y/self.block_size[1])] for y in range(self.base_dims[1])] for x in range(self.base_dims[0])]


class CarPhysics:

    MAX_SPEED = 10
    STEERING_FORCE = 0.03

    CLEAR_COLOR = (0, 0, 0)
    CAR_COLOR = (80, 80, 255)
    ARROW_COLOR = (255, 255, 80)

    LIDAR_OFFSET = 0
    LIDAR_RANGE = [-math.pi/2, math.pi/2]
    LIDAR_P = 16

    STATE_HISTORY = 5

    HISTORY_MOD = 16

    SPEED_AVG = 240

    def __init__(self, width, length, terrain, distancer):
        self.width = width
        self.length = length
        self.height = length
        self.terrain = terrain
        self.rotation = self.terrain.get_start_rotation()
        self.center = [width // 2, length // 2]
        self.direction = 0
        self.pos_x, self.pos_y = self.terrain.get_start_pos()
        self.speed = 0
        self.ACTIONS = [self.go_forward, self.go_backward, self.turn_right_full, self.turn_left_full]

 
        self.car_surface = py.Surface((self.width, self.height))
        self.car_surface.set_colorkey(self.CLEAR_COLOR)
        self.car_surface.fill(self.CAR_COLOR)
        py.draw.polygon(self.car_surface, self.ARROW_COLOR, [(self.width*0.5, self.height*0.2), (self.width*0.5, self.height*0.8), (self.width*0.9, self.height*0.5)], 1)
        self.car_copy = self.car_surface.copy()
        self.car_copy.set_colorkey(self.CLEAR_COLOR)
        self.rect = self.car_copy.get_rect()
        self.go_forward()
        self.previous_speeds = []
        self.average_speed = 0
        self.compute_avg_speed()
        self.move_from_start = [0, 0]
        self.last_reward = 0
        self.last_lidar_score = 0
        self.last_speed_score = 0
        self.distancer = distancer
        if self.distancer is not None:
            self.base_distance = self.distancer.get_distance(self.pos_x, self.pos_y)
        else:
            self.base_distance = 0
        self.last_distance_score = self.base_distance
        self.total_steps = 0
        self.previous_states = []
        self.history_time = 0
    
    def set_pos_rot(self, pos_x, pos_y, rot):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rotation = rot

    def compute_avg_speed(self):
        self.previous_speeds.append(self.speed)
        self.previous_speeds = self.previous_speeds[max(0, len(self.previous_speeds) - self.SPEED_AVG):]
        self.average_speed = sum(self.previous_speeds)/len(self.previous_speeds)
    
    def compute_dist_from_start(self, dx, dy):
        self.move_from_start = [self.move_from_start[0] + dx, self.move_from_start[1] + dy]

    def reset(self):
        self.rotation = self.terrain.get_start_rotation()
        self.pos_x, self.pos_y = self.terrain.get_start_pos()
        self.speed = 0
        self.direction = 0
        self.go_forward()
        self.compute_avg_speed()
        self.move_from_start = [0, 0]
        self.last_reward = 0
        self.last_lidar_score = 0
        self.last_speed_score = 0
        self.last_distance_score = self.base_distance
        self.total_steps = 0
        self.previous_states = []
        self.history_time = 0
        return self.get_state()
    
    def get_state(self):
        #return self.lid_scan() + [self.speed, self.direction]
        if self.history_time % self.HISTORY_MOD == 0:
            if len(self.previous_states) >= 6:
                self.previous_states = self.previous_states[6:]
            while len(self.previous_states) < self.STATE_HISTORY * 6:
                self.previous_states += self.lid_scan() + [self.speed, self.direction]
        else:
            self.previous_states = self.previous_states[:-6]
            self.previous_states += self.lid_scan() + [self.speed, self.direction]
        #print(self.previous_states)
        return self.previous_states
        
    
    def cast_ray(self, x, y, angle):
        dx = math.cos(angle)
        dy = math.sin(angle)
        done = False
        dist = 1
        while not done:
            done = self.terrain.is_wall(int(x + dist*dx), int(y + dist*dy))
            dist += 2
        return dist

    def lid_scan(self):
        angles = [-math.pi/4, 0, math.pi/4, math.pi]
        return [self.cast_ray(self.pos_x, self.pos_y, self.LIDAR_OFFSET + self.rotation + angle) for angle in angles]

    """
    def lid_scan(self):
        return [self.cast_ray(self.pos_x, self.pos_y, self.LIDAR_OFFSET - math.pi/2 + self.rotation + i*(self.LIDAR_RANGE[1] - self.LIDAR_RANGE[0])/self.LIDAR_P) for i in range(self.LIDAR_P)]
    """

    def draw(self, surface, font, total_reward, current_reward=0, current_distance=0):
        image = py.transform.rotate(self.car_surface, math.pi/2 -self.rotation*180/math.pi)
        rect = image.get_rect(center = (int(self.pos_x), int(self.pos_y)))
        surface.blit(image, rect)
        text_surface = font.render(f"RWD: {current_reward:.3f} TRD: {total_reward:.3f} DST: {current_distance:.3f}", False, (20, 20, 20))
        surface.blit(text_surface, (10,10))

    def rotate_point_center(self, x, y, rot):
        return [(x - self.center[0])*math.cos(rot) - (y - self.center[1])*math.sin(rot),
            (x - self.center[0])*math.sin(rot) + (y - self.center[1])*math.cos(rot)]

    def check_collide_terrain(self, pos, rot):
        points = [self.rotate_point_center(x, (y%2)*self.height, rot) for x in range(0, self.width, 2) for y in range(2)]
        points += [self.rotate_point_center((x%2)*self.width, y, rot) for y in range(0, self.height, 2) for x in range(2)]
        collisions = [self.terrain.is_wall(int(point[0] + pos[0]), int(point[1] + pos[1])) for point in points]
        #print(collisions)
        return True in collisions
    
    def get_reward(self, state):
        self.compute_avg_speed()
        #self.last_lidar_score = 2*math.log2(0.4 + state[int(self.LIDAR_P/2)]/100)
        self.last_speed_score = 0.3*(max(0, abs(self.average_speed) - 5))

        #distance_to_goal = 10*(1 - (self.distancer.get_distance(self.pos_x, self.pos_y)/self.base_distance))

        current_distance = self.distancer.get_distance(self.pos_x, self.pos_y)#/self.base_distance
        #self.last_lidar_score = self.last_speed_score
        distance_score = 1 if self.last_distance_score - current_distance + self.last_lidar_score >= 0 else -1
        self.last_lidar_score = (distance_score - 1) / 2
        self.last_distance_score = current_distance #if distance_score > 0 else self.last_distance_score #self.distancer.get_distance(self.pos_x, self.pos_y)/self.base_distance
        self.last_speed_score = self.last_distance_score
        #final_score = 1 if self.average_speed > 8 else -1
        return distance_score #if self.average_speed > 2.5 else -1 #1.75 if final_score + distance_score == 2 else -1
        #return self.last_lidar_score + distance_to_goal #0.1*math.sqrt(self.move_from_start[0]**2 + self.move_from_start[1]**2)* self.last_speed_score * self.last_lidar_score

    def update(self, action, dt):
        self.total_steps += 1
        self.history_time += 1
        self.ACTIONS[action]()
        
        state = self.get_state()


        r_t = math.fmod(self.rotation - self.speed*self.direction*dt*self.STEERING_FORCE/(1 + self.speed**2), 2*math.pi)
        x_t = self.pos_x + dt*self.speed*math.cos(r_t)
        y_t = self.pos_y + dt*self.speed*math.sin(r_t)
        self.compute_dist_from_start(x_t - self.pos_x, y_t - self.pos_y)
        self.last_reward = self.get_reward(state)
        if self.check_collide_terrain([x_t, y_t], r_t):
            print("DONE", self.average_speed, self.get_reward(state))
            end_reward = - 20*60 #if self.distancer.get_distance(self.pos_x, self.pos_y)/self.base_distance > 0.5 else 300
            print("RWD", end_reward)
            return state, end_reward, True, None
        else:
            self.pos_x = x_t
            self.pos_y = y_t
            self.rotation = r_t
            return state, self.get_reward(state), False, None

    def go_forward(self):
        self.speed = self.MAX_SPEED
    
    def stop(self):
        self.speed = 0

    def go_backward(self):
        self.speed = - self.MAX_SPEED
    
    def turn(self, direction):
        self.direction = min(100, max(direction, -100))

    def turn_right(self, amount):
        self.direction = min(self.direction + amount, 100)
    
    def turn_right_full(self):
        self.direction = 100
    
    def turn_left_full(self):
        self.direction = -100
    
    def turn_left(self, amount):
        self.direction = max(self.direction - amount, -100)