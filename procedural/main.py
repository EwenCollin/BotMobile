import math

class Driver:

    NB_RAYS = 17

    MAX_DIR = 2 + 487*0.0005

    MAX_SPEED = 0.05 + 487*0.0005

    def __init__(self):
        pass

    def predict(self, observation, *args):
        angles = [math.pi/4 +  i*math.pi/(2*self.NB_RAYS) for i in range(self.NB_RAYS)]
        cos_angles = [math.cos(angle) for angle in angles]
        sin_angles = [math.sin(angle) for angle in angles]

        direction = -1*sum([observation[i]*cos_angles[i] for i in range(self.NB_RAYS)])/self.MAX_DIR

        direction = min(1, max(-1, direction))

        speed = sum([observation[i]*sin_angles[i] for i in range(self.NB_RAYS)])/self.MAX_SPEED - 0.4

        speed *= 0.01

        speed = min(1, max(-1, speed))

        return [speed, direction]