"""Peachy Geometry

Geometric shape representations. The majority of these shapes are for
convenience, except for Rect which is used extensively throughout peachy (a
primary example being peachy.Entity).
"""


import copy
import math


def distance_between_points(point_one, point_two):
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


def distance_between_shapes(shape_a, shape_b):
    """Returns int, the distance between the center of two peachy.geo shapes."""
    point_one = None
    point_two = None

    try:
        point_one = shape_a.center
    except ValueError:
        point_one = (shape_a[0], shape_a[1])

    try:
        point_two = shape_b.center
    except ValueError:
        point_two = (shape_b[0], shape_b[1])

    return distance_between_points(point_one, point_two)


class Shape(object):
    def at_point(self, x=None, y=None):
        """Return a copy of a shape at a specified point.

        The purpose of this function is to move a shape before doing collision
        checks on it.

        Args:
            x (int, optional): The x coordinate to relocate to.
            y (int, optional): The y coordinate to relocate to.

        Returns:
            Shape: a copy of the shape object that has been relocated.
        """
        working_shape = copy.copy(self)
        if x is not None:
            working_shape.x = x
        if y is not None:
            working_shape.y = y
        return working_shape


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
        return distance_between_points(self.p1, self.p2)


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

    def __getitem__(self, i):
        return self.ls()[i]

    def __iter__(self):
        for attribute in self.ls():
            yield attribute

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.width = value
        elif index == 3:
            self.height = value

    def __str__(self):
        return "({}, {}, {}, {})"\
            .format(self.x, self.y, self.width, self.height)

    def ls(self):
        """Return as list: [x, y, width, height]."""
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
