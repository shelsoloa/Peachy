"""Peachy Geometry

Geometric shape representations. The majority of these shapes are for
convenience, except for Rect which is used extensively throughout peachy (a
primary example being peachy.Entity).
"""


import math


def distance(point_one, point_two):
    """Calculate the distance between two points.

    Args:
        point_one (tuple[int, int], peachy.geo.Point)
        point_two (tuple[int, int], peachy.geo.Point)

    Return:
        int: The distance between the two points provided.
    """
    xa, ya = point_one
    xb, yb = point_two
    return math.sqrt(math.pow(xb - xa, 2) + math.pow(yb - ya, 2))


class Shape(object):
    pass


class Circle(Shape):
    """2D Circle

    Attributes:
        x (int): The x-coordinate of the circle.
        y (int): The y-coordinate of the circle.
        radius (int): The radius of the circle.
    """
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        if isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1] and \
                self.radius == other[3]

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.radius

    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.radius)

    @property
    def center(self):
        """Get the center point of the circle.

        Returns:
            tuple (int, int): center x and center y, respectively.
        """
        return self.center_x, self.center_y

    @property
    def center_x(self):
        """Returns int, the center x-coordinate of the circle."""
        return self.x + self.radius

    @property
    def center_y(self):
        """Returns int, the center y-coordinate of the circle."""
        return self.y + self.radius

    @property
    def diameter(self):
        """The diameter of the circle."""
        return self.radius * 2

    @diameter.setter
    def diameter(self, diameter):
        self.radius = diameter / 2

    def contains(self, x, y):
        """"Returns True, if the point (x, y) lies within the circle."""
        return self.distance_from_point(x, y) <= self.radius

    def distance_from_point(self, x, y):
        """The distance, in pixels, from self.center to the point (x, y)."""
        return math.sqrt(math.pow(self.center_x - x, 2) +
                         math.pow(self.center_y - y, 2))


class Line(Shape):
    """2D Line

    Attributes:
        p1 (peachy.geo.Point): The first point of the line.
        p2 (peachy.geo.Point): The second point of the line.
    """
    def __init__(self, x1, y1, x2, y2):
        self.p1 = Point(x1, y1)
        self.p2 = Point(x2, y2)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        if isinstance(other, tuple):
            return self.p1.x == other[0] and self.p1.y == other[1] \
                and self.p2.x == other[2] and self.p2.y == other[3]

    def __iter__(self):
        yield self.p1.x
        yield self.p1.y
        yield self.p2.x
        yield self.p2.y

    def __str__(self):
        return "{}, {}".format(self.p1, self.p2)

    @property
    def center(self):
        """Get the center point of the line.

        Returns:
            int, int: center x and center y, respectively.
        """
        return (self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2

    @property
    def length(self):
        """Returns int, the length of the line."""
        return distance(self.p1, self.p2)


class Point(Shape):
    """2D Point

    Attributes:
        x (int): The x-coordinate.
        y (int): The y-coordinate.
    """
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        if isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]

    def __iter__(self):
        yield self.x
        yield self.y

    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)

    @property
    def center(self):
        return (self.x, self.y)


class Rect(Shape):
    """2D Rectangle

    Attributes:
        x (int): X coordinate of rectangle
        y (int): Y coordinate of rectangle
        width (int): Width of rectangle
        height (int): Height of rectangle
    """
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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        if isinstance(other, tuple):
            return self.x == other[0] and \
                self.y == other[1] and \
                self.width == other[2] and \
                self.height == other[3]

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.width
        yield self.height

    def __str__(self):
        return "({}, {}, {}, {})"\
            .format(self.x, self.y, self.width, self.height)

    def ls(self):
        """ Return as list: [x, y, width, height] """
        return [self.x, self.y, self.width, self.height]

    @property
    def bottom(self):
        """The bottom of rectangle (y-axis).
        Semantic sugar for self.y + self.height.
        """
        return self.y + self.height

    @bottom.setter
    def bottom(self, bottom):
        self.y = bottom - self.height

    @property
    def center(self):
        """The center point of the rectangle.

        Returns:
            tuple (int, int): x and y coordinates for center of rectangle.
        """
        return self.center_x, self.center_y

    @property
    def center_x(self):
        """Center of rect (x-axis)."""
        return self.x + self.width / 2

    @center_x.setter
    def center_x(self, cx):
        self.x = cx - self.width / 2

    @property
    def center_y(self):
        """Center of rect (y-axis)."""
        return self.y + self.height / 2

    @center_y.setter
    def center_y(self, cy):
        self.y = cy - self.height / 2

    @property
    def half_width(self):
        return self.width / 2

    @property
    def half_height(self):
        return self.height / 2

    @property
    def left(self):
        """The left side of rectangle (x-axis).
        Semantic sugar for self.x.
        """
        return self.x

    @left.setter
    def left(self, left):
        self.x = left

    @property
    def right(self):
        """The right side of rectangle (x-axis).
        Semantic sugar for self.x + self.width.
        """
        return self.x + self.width

    @right.setter
    def right(self, right):
        self.x = right - self.width

    @property
    def top(self):
        """The top of rectangle (y-axis)
        Semantic sugar for self.y.
        """
        return self.y

    @top.setter
    def top(self, top):
        self.y = top

    def collides(self, other, x, y):
        """Check if 'self' is colliding with a rectangle.

        Args:
            other (peachy.Rect): The rect to check for collision.
            x (int): The x-coordinate to use for this rectangle.
            y (int): The y-coordinate to use for this rectangle.

        Returns:
            bool: True, if collision is occuring.

        Raises:
            AttributeError: The object provided was invalid.
        """

        try:
            ox, oy, owidth, oheight = other

            right_a = x + self.width
            bottom_a = y + self.height
            right_b = ox + owidth
            bottom_b = oy + oheight

            if x < right_b and \
               right_a > ox and \
               y < bottom_b and \
               bottom_a > oy:
                return True
            else:
                return False

        except AttributeError:
            print("Invalid object passed to collides function.")
            return False

    def collides_circle(self, circle, x=None, y=None):
        """Check if 'self' is colliding with a circle

        Args:
            circle (peachy.geo.Circle, tuple[x, y, r]): The circle to check for
                collision. Represented using a Circle or tuple.
            x (int, optional): Override for self.x.
            y (int, optional): Override for self.y.
        """
        if x is None or y is None:
            x = self.x
            y = self.y

        circle_x, circle_y, radius = circle
        circle_x += radius
        circle_y += radius

        rx = x + self.width / 2
        ry = y + self.height / 2

        dist_x = abs(circle_x - rx)
        dist_y = abs(circle_y - ry)
        half_width = self.width / 2
        half_height = self.height / 2

        if dist_x > (half_width + radius) or \
           dist_y > (half_height + radius):
            return False

        if dist_x <= half_width or \
           dist_y <= half_height:
            return True

        corner_distance = (dist_x - half_width)**2 + (dist_y - half_height)**2

        return corner_distance <= (radius**2)

    def collides_point(self, point, x=None, y=None):
        """Check if 'self' is colliding with a point.

        Args:
            point (peachy.geo.Point, tuple[x, y]): The point represented by
                either a peachy Point or a tuple.
            x (int, optional): Override for self.x
            y (int, optional): Override for self.y
        """
        if x is None or y is None:
            x = self.x
            y = self.y

        px, py = point
        if x <= px <= x + self.width and y <= py <= y + self.height:
            return True
        else:
            return False

    def collides_rect(self, rect, x=None, y=None):
        """Check if 'self' is colliding with a rectangle.

        Args:
            rect (peachy.geo.Rect, tuple[x, y, width, height]): The rectangle
                represented by either a peachy Point or tuple.
            x (int, optional): Override for self.x
            y (int, optional): Override for self.y
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

    def distance_from_shape(self, other):
        """Returns int, the distance in pixels, between the center of self and
        a geo object (peachy.geo.Shape)
        """
        ox, oy = other.center
        return self.distance_from_point(ox, oy)

    def distance_from_rect(self, r):
        """Returns int, the distance in pixels between the center of self and
        a rectangle.
        """
        sx, sy = self.center
        ox, oy = r.center
        a = abs(sx - ox)
        b = abs(sy - oy)
        return math.sqrt(a**2 + b**2)

    def distance_from_point(self, px, py):
        """Returns int, the distance in pixels between center and a point."""
        a = abs(self.center_x - px)
        b = abs(self.center_y - py)
        return math.sqrt(a**2 + b**2)
