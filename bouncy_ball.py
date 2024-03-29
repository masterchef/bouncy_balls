import click
import base_sense_hat_app
from sense_hat import SenseHat
import datetime
import numpy
import random

from ball import Ball
from vector import Vector

BLACK_PIXEL = [0, 0, 0]
RANDOM = 'random'

class BouncyBalls(base_sense_hat_app.SenseHatAnimation):
    def __init__(self, mode=RANDOM, ball_count=5, reinit=False, duration=10, torus=False):
        super(BouncyBalls,self).__init__(duration=duration, reinit=reinit)
        self.board = Board(torus=torus)
        self.mode = mode
        self.ball_count = ball_count
    
    def setup(self):
        self.reset()
        if self.mode == RANDOM:
            for i in xrange(self.ball_count):
                self.add_random_ball()
        else:
            input_string = 'Please enter ball speed, angle, x and y coordinates or nothing if finished: '
            raw = raw_input(input_string)
            while raw != '':
                speed, angle, x, y = raw.split(',')
                self.add_ball(speed=int(speed), angle=int(angle), coordinates=(int(x), int(y)))
                raw = raw_input(input_string)

    def run(self):
        pixel_list = self.board.run()
        self.renderer.set_pixels(pixel_list)

    def add_ball(self, speed=10, angle=0, color=None, coordinates=(0, 0)):
        if not color:
            color = self.generate_color()
        ball = Ball(x=coordinates[0], y=coordinates[1], vector=Vector(angle, speed), color=color)
        self.board.add_ball(ball)

    def add_random_ball(self):
        speed = random.randint(1, 30)
        angle = random.randint(-360, 360)
        color = self.generate_color()
        x = random.randint(0, self.board.w - 1)
        y = random.randint(0, self.board.h - 1)
        ball = Ball(x, y, vector=Vector(angle, speed), color=color)
        self.board.add_ball(ball)

    def generate_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return [r, g, b]

    def reset(self):
        self.board.remove_all()


class Board(object):
    def __init__(self, w=8, h=8, torus=False):
        self.w = w
        self.h = h
        self.board = numpy.ndarray(shape=(w, h), dtype=list)
        self.board.fill(BLACK_PIXEL)
        self.balls = {}
        self.torus = torus

    def run(self):
        for id, ball in self.balls.iteritems():
            self.board[ball.x][ball.y] = BLACK_PIXEL
            new_x, new_y = self.update_ball(ball)
            self.board[new_x][new_y] = ball
        return self.render()

    def add_ball(self, ball):
        ball.prepare_for_bounce()
        self.balls[ball.id] = ball

    def remove_ball(self, ball):
        self.balls.pop(ball.id)

    def remove_all(self):
        self.balls = {}
        self.board.fill(BLACK_PIXEL)

    def render(self):
        return map(lambda x: x.color if isinstance(x, Ball) else x, [item for sublist in self.board for item in sublist])

    def is_empty(self, x, y):
        if x < self.w and y < self.h and x >= 0 and y >= 0:
            return self.board[x][y] == BLACK_PIXEL
        else:
            raise Exception('Board out of bounds: {0}:{1}'.format(x, y))
    
    def update_ball(self, ball):
        passed_time = (datetime.datetime.now() - ball.last_change).microseconds / 1000000.0
        distance = ball.move_speed() * passed_time
        x_delta, y_delta = ball.calculate_delta(distance)
        new_x, new_y = ball.calculate_new_coordinate(x_delta, y_delta)
        # Check if we're outside the bounds
        collided = self.check_collisions(ball, new_x, new_y)
        if collided:
            x_delta, y_delta = ball.calculate_delta(distance)
            new_x, new_y = ball.calculate_new_coordinate(x_delta, y_delta)
        
        # Update real coordinates
        ball.real_x += x_delta
        ball.real_y += y_delta
        ball.last_change = datetime.datetime.now()
        if new_x != ball.x or new_y != ball.y:
            ball.update_coordinates(new_x, new_y)
        return ball.x, ball.y

    def check_collisions(self, ball, new_x, new_y):
        hit_wall = False
        if not self.torus and (new_x >= self.w or new_x < 0):
            ball.move_angle(180 - ball.move_angle())
            hit_wall = True
        if not self.torus and (new_y >= self.h or new_y < 0):
            ball.move_angle(360 - ball.move_angle())
            hit_wall = True

        if self.torus and new_x >= self.w:
            new_x = 0 + new_x - self.w;
        if self.torus and new_x < 0:
            new_x = self.w + new_x
        if self.torus and new_y >= self.h:
            new_y = 0 + new_y - self.h
        if self.torus and new_y < 0:
            new_y = self.h + new_y

        if not hit_wall and not self.is_empty(new_x, new_y):
            return ball.resolve_collision(self.board[new_x][new_y])

        return hit_wall

@click.group()
def cli():
    pass


@cli.command()
@click.option('--ball-count', default=5, help='Number of balls to generate')
@click.option('--reinit', default=False, help='Reinitiate between runs')
@click.option('--duration', default=None, help='Duration for each run')
def demo(ball_count, reinit, duration):
    real_sense = SenseHat()
    real_sense.low_light = True
    sense_app = base_sense_hat_app.SenseHatApp(real_sense)
    bb = BouncyBalls(ball_count=ball_count, reinit=reinit, duration=duration)
    sense_app.register(bb)
    sense_app.run()


@cli.command()
def manual():
    real_sense = SenseHat()
    real_sense.low_light = True
    sense_app = base_sense_hat_app.SenseHatApp(real_sense)
    bb = BouncyBalls(mode='manual')
    sense_app.register(bb)
    sense_app.run()

if __name__ == '__main__':
    cli()
