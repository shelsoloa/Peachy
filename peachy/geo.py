import math


# Base Shape class
# Circle
# Line
# Polygon


class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        if isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]


class Rect(object):
    def __init__(self, x, y, width=None, height=None):
        if width is None or height is None:
            width = x
            height = y
            x = 0
            y = 0

        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def ls(self):
        """ Return as list: [x, y, width, height] """
        return [self.x, self.y, self.width, self.height]

    @property
    def bottom(self):
        return self.y + self.height

    @bottom.setter
    def bottom(self, bottom):
        self.y = bottom - self.height

    @property
    def center(self):
        """ Return center coordinates of entity in a tuple """
        return (self.x + self.width / 2, self.y + self.height / 2)

    @property
    def center_x(self):
        return self.x + self.width / 2

    @center_x.setter
    def center_x(self, cx):
        self.x = cx - self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    @center_y.setter
    def center_y(self, cy):
        self.y = cy - self.height / 2

    def collides(self, e, x, y):
        """ Check if 'self' is colliding with another Rect """

        try:
            right_a = x + self.width
            bottom_a = y + self.height
            right_b = e.x + e.width
            bottom_b = e.y + e.height

            if x < right_b and \
               right_a > e.x and \
               y < bottom_b and \
               bottom_a > e.y:
                return True
            else:
                return False

        except AttributeError:
            print("Invalid object passed to collides function.")
            return False

    def collides_circle(self, circle, x=None, y=None):
        """
        Check if 'self' is colliding with a circle
        circle = tuple (x, y, radius)

        Can provide custom x/y or leave blank for self.x/self.y.
        """
        if x is None or y is None:
            x = self.x
            y = self.y

        circle_x, circle_y, radius = circle
        circle_x += radius
        circle_y += radius

        rx = self.x + self.width / 2
        ry = self.y + self.height / 2

        dist_x = abs(circle_x - rx)
        dist_y = abs(circle_y - ry)
        half_width = self.width / 2
        half_height = self.height / 2

        if dist_x > (half_width + radius):
            return False
        if dist_y > (half_height + radius):
            return False

        if dist_x <= half_width:
            return True
        if dist_y <= half_height:
            return True

        corner_distance = (dist_x - half_width)**2 + (dist_y - half_height)**2

        return corner_distance <= (radius**2)

    def collides_point(self, point, x=None, y=None):
        """ Check if 'self' is colliding with a specific point """
        if x is None or y is None:
            x = self.x
            y = self.y

        px, py = point
        if x <= px <= x + self.width and y <= py <= y + self.height:
            return True
        else:
            return False

    def collides_rect(self, rect, x=None, y=None):
        """
        Check if 'self' is colliding with a rectangle.
        rect = tuple (x, y, width, height)

        Can provide custom x/y or leave blank for self.x/self.y
        """
        if x is None or y is None:
            x = self.x
            y = self.y

        rx, ry, rwidth, rheight = rect

        left_a = x
        right_a = x + self.width
        top_a = y
        bottom_a = y + self.height

        left_b = rx
        right_b = rx + rwidth
        top_b = ry
        bottom_b = ry + rheight

        if (bottom_a <= top_b or top_a >= bottom_b or
                right_a <= left_b or left_a >= right_b):
            return False
        else:
            return True

    def distance_from(self, other):
        """
        Get the distance in pixels between the center of two Rect/Entity
        objects.
        """
        sx, sy = self.center
        ox, oy = other.center
        a = abs(sx - ox)
        b = abs(sy - oy)

        return math.sqrt(a**2 + b**2)

    def distance_from_point(self, px, py):
        """
        Get the distance in pixels between the center of this object and a
        point.
        """
        a = abs(self.x - px)
        b = abs(self.y - py)
        return math.sqrt(a**2 + b**2)
