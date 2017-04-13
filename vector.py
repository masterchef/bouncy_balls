import math


class Vector(object):
    def __init__(self, angle=0, speed=0):
        self.angle = angle
        self.speed = speed

    def get_rate(self):
        if self.speed > 0:
            return 1.0 / self.speed
        else:
            return None

    def update(self, x, y):
        self.speed = math.sqrt(x**2 + y**2)
        print "Update velocity: {0}, {1}, curr_angle: {2}".format(x, y, self.angle)
        angle = math.degrees(math.atan(y/x))
        # First quadrant
        if x >= 0 and y >= 0:
            self.angle = angle
        # Second quandrant
        if x <= 0 and y >= 0:
            self.angle = 180 - angle
        # Third quadrant
        if x < 0 and y < 0:
            self.angle = 180 + angle
        # Fourth
        if x >=0 and y < 0:
            self.angle = 360 - angle

        print "New: {0}".format(self.angle)

    def get_angle(self, degrees=False):
        if degrees:
            return self.angle
        else:
            return math.radians(self.angle)
    
def calculate_new_speed(m1, u1, m2, u2):
    v1 = (u1*(m1 - m2) + 2*m2*u2) / (m1 + m2)
    v2 = (u2*(m1 - m2) + 2*m2*u1) / (m1 + m2)
    return v1, v2

