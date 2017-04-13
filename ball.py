import uuid
import datetime
import math
import logging
from vector import calculate_new_speed

log = logging.getLogger(__name__)

class Ball(object):
    def __init__(self, x=0, y=0, vector=None, color=[255, 255, 255], mass=1, enable_collision=False):
        self.x = x
        self.y = y
        self.mass = mass
        self.real_x = x
        self.real_y = y
        self.vector = vector
        self.last_change = None
        self.color = color
        self.id = uuid.uuid1()
        log.info('Initializing ball: {0}:{1}, id: {2}'.format(x, y, self.id))

    def update_coordinates(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        #print "New coords: x:{0}, y:{1}".format(new_x, new_y)
        #print "New real coords: x:{0}, y:{1}".format(self.real_x, self.real_y)

    def calculate_new_coordinate(self, x_delta, y_delta):
        new_x = round(self.real_x + x_delta, 0)
        new_y = round(self.real_y + y_delta, 0)
        return new_x, new_y

    def calculate_delta(self, distance):
        x_delta = math.cos(self.vector.get_angle()) * distance
        y_delta = math.sin(self.vector.get_angle()) * distance
        return x_delta, y_delta

    def prepare_for_bounce(self):
        self.last_change = datetime.datetime.now()

    def coordinates(self):
        return self.x, self.y

    def move_rate(self):
        return self.vector.get_rate()

    def move_speed(self):
        return self.vector.speed

    def move_angle(self, angle=None, deg=True):
        if angle is not None:
            self.vector.angle = angle
        else:
            return self.vector.get_angle(degrees=deg)

    def update_velocity(self, vx, vy):
        self.vector.update(vx, vy)

    def resolve_collision(self, ball):
        v1x = math.cos(self.move_angle(deg=False)) * self.move_speed()
        v1y = math.sin(self.move_angle(deg=False)) * self.move_speed()
        v2x = math.cos(ball.move_angle(deg=False)) * ball.move_speed()
        v2y = math.sin(ball.move_angle(deg=False)) * ball.move_speed()

        print "v1x: {0}, v1y: {1}     -     v2x: {2}, v2y: {3}".format(v1x, v1y, v2x, v2y)
        new_v1x, new_v2x = calculate_new_speed(self.mass, v1x, ball.mass, v2x)
        new_v1y, new_v2y = calculate_new_speed(self.mass, v1y, ball.mass, v2y)

        print "v1x: {0}, v1y: {1}     -     v2x: {2}, v2y: {3}".format(new_v1x, new_v1y, new_v2x, new_v2y)
        self.update_velocity(new_v1x, new_v1y)
        ball.update_velocity(new_v2x, new_v2y)


