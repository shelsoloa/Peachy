# Collision functions are alphabetical but prioritze rectangles because
# they are most common
"""The max tolerance for floating point errors."""
TOLERANCE = 0.001


def is_between(x, a, b):
    return min(a, b) <= x <= max(a, b)


def rect_to_vector_segments(rect):
    x, y, width, height = rect
    top = (x, y, width, 0)
    right = (x + width, y, 0, height)
    bottom = (x + width, y + height, -width, 0)
    left = (x, y + height, 0, -height)
    return (top, right, bottom, left)


class CollisionResult(object):
    def __init__(self, f, a, b):
        self.collision_function = f
        self.shape_a = a
        self.shape_b = b


def get_collision_function(shape_a, shape_b):
    from peachy.geo import ShapeEnum

    collision_function = None

    if shape_a.shapeid > shape_b.shapeid:
        shape_a, shape_b = shape_b, shape_a

    if shape_a.shapeid == ShapeEnum.RECT:
        if shape_b.shapeid == ShapeEnum.RECT:
            collision_function = rect_rect
        elif shape_b.shapeid == ShapeEnum.CIRCLE:
            collision_function = rect_circle
        elif shape_b.shapeid == ShapeEnum.LINE:
            collision_function = rect_line
        elif shape_b.shapeid == ShapeEnum.POINT:
            collision_function = rect_point
    elif shape_a.shapeid == ShapeEnum.CIRCLE:
        if shape_b.shapeid == ShapeEnum.RECT:
            collision_function = rect_circle
        elif shape_b.shapeid == ShapeEnum.CIRCLE:
            collision_function = circle_circle
        elif shape_b.shapeid == ShapeEnum.LINE:
            collision_function = circle_line
        elif shape_b.shapeid == ShapeEnum.POINT:
            collision_function = circle_point
    elif shape_a.shapeid == ShapeEnum.LINE:
        if shape_b.shapeid == ShapeEnum.RECT:
            collision_function = rect_line
        elif shape_b.shapeid == ShapeEnum.CIRCLE:
            collision_function = circle_line
        if shape_b.shapeid == ShapeEnum.LINE:
            collision_function = line_line
        elif shape_b.shapeid == ShapeEnum.POINT:
            collision_function = line_point
    elif shape_a.shapeid == ShapeEnum.POINT:
        if shape_b.shapeid == ShapeEnum.RECT:
            collision_function = rect_point
        elif shape_b.shapeid == ShapeEnum.CIRCLE:
            collision_function = circle_point
        elif shape_b.shapeid == ShapeEnum.POINT:
            collision_function = point_point
        elif shape_b.shapeid == ShapeEnum.LINE:
            collision_function = line_point
    # elif shape_a.shapeid == POLYGON_ID:
    #     pass

    return collision_function


def collides_first(container, main_shape):
    for shape in container:
        result = collides_unknown(main_shape, shape)
        if result:
            return result
    return False


def collides_group(container, group, shape, collision_function=None):
    """Check if a shape is colliding with a group of shapes.

    Check if self is colliding with any entity that is a member of the
    specified group.

    Args:
        group (str): The name of the group to survey.
        x (int, optional): Temporary replacement x coordinate for self.
        y (int, optional): Temporary replacement y coordinate for self.

    Returns:
        list[peachy.collision.CollisionResult]: A list of CollisionResults
            containing the colliding entities and the function used to detect
            collision.

    Todo:
        * Enable collision_function overload
    """

    collisions = []
    shapes = container.get_group(group)

    collision_type = None
    collision = None
    for test in shapes:
            if shape is test:
                continue

            if collision_type != test.shapeid:
                collision = get_collision_function(shape, test)

            if shape.shapeid < test.shapeid:
                a, b = shape, test
            else:
                a, b = test, shape

            if collision(a, b):
                collisions.append(CollisionResult(collision, a, b))

    return collisions


def collides_groups(container, groups, main_shape, collision_function=None):
    """Check if colliding with groups.

    Check if a shape is colliding with any shape that is a member of any
    of the groups specified.

    Args:
        container (peachy.Room): The room the shapes are held in
        main_shape (peachy.Shape): The shape to use as target
        groups (list[str]): A string list of group names to survey.
        collision_function (function, optional): A function to use for
            collision detection. Can be any of the functions in
            peachy.collisions or a custom function. Shape must be compatible.

    Returns:
        list[peachy.Entity]: Every entity colliding with main_shape that is a
            member of any of the specified groups.
    """

    collisions = []
    shapes = container.get_group(*groups)
    if len(shapes) > 0:
        if collision_function is None:
            collision = get_collision_function(main_shape, shapes[0])
        else:
            collision = collision_function

        for test in shapes:
            if collision(main_shape, test):
                collisions.append(CollisionResult(collision, main_shape, test))

    return collisions


def collides_multiple(container, main_shape):
    collisions = []
    for shape in container:
        if main_shape is not shape and collides_unknown(main_shape, shape):
            collisions.append(shape)
    return collisions


def collides_name(container, shape, name):
    """Check if colliding with named entity.

    Args:
        name (str): The name of the entity to check

    Returns:
        peachy.geo.Shape: Returns shape if colliding or None if no collision.
    """

    target = container.get_name(name)
    if target:
        result = collides_unknown(shape, target)
        if result:
            return result
    return None


def collides_unknown(shape_a, shape_b):
    collision = get_collision_function(shape_a, shape_b)
    if collision(shape_a, shape_b):
        return CollisionResult(collision, shape_a, shape_b)
    else:
        return None


def collides_solid(container, main_shape):
    """Check if colliding with any solid entity.

    Checks if self collides with any entity that has Entity.solid set as
    True.

    Args:

    Returns:
        list[peachy.Entity]: Every solid entity colliding with self.
    """
    collisions = []
    for shape in container:
        if shape is not main_shape and shape.active and shape.solid:
            result = collides_unknown(main_shape, shape)
            if result:
                collisions.append(result)
    return collisions


def circle_circle(circle_a, circle_b):
    ax, ay, ar = circle_a
    bx, by, br = circle_b

    ax += ar
    ay += ar
    bx += br
    by += br

    return (ax - bx)**2 + (ay - by)**2 <= (ar + br)**2


def circle_line(circle, line):
    cx, cy, cr = circle
    x1, y1, x2, y2 = line

    a = (cx + cr, cy + cr)
    b = closest_point_on_line(line, a)

    return (b[0] - a[0])**2 + (b[1] - a[1])**2 <= cr**2


def circle_point(circle, point):
    circle_x, circle_y, circle_r = circle
    circle_x += circle_r
    circle_y += circle_r

    point_x, point_y = point

    return (circle_x - point_x)**2 + (circle_y - point_y)**2 <= circle_r**2


def line_line(line_a, line_b):
    a_x1, a_y1, a_x2, a_y2 = line_a
    b_x1, b_y1, b_x2, b_y2 = line_b

    denominator = ((b_y2 - b_y1) * (a_x2 - a_x1)) - \
                  ((b_x2 - b_x1) * (a_y2 - a_y1))

    if denominator == 0:
        return False
    else:
        ua = (((b_x2 - b_x1) * (a_y1 - b_y1)) -
              ((b_y2 - b_y1) * (a_x1 - b_x1))) / denominator

        ub = (((a_x2 - a_x1) * (a_y1 - b_y1)) -
              ((a_y2 - a_y1) * (a_x1 - b_x1))) / denominator

        if (ua < 0) or (ua > 1) or (ub < 0) or (ub > 1):
            return False
        return True


def line_point(line, point):
    px, py = point
    x1, y1, x2, y2 = line

    if (is_between(px, x1, x2) and is_between(py, y1, y2)):
        # y = ax + b
        if x2 - x1 == 0:
            return True
        elif y2 - y1 == 0:
            return True
        a = (y2 - y1) / (x2 - x1)  # slope
        b = y1 - a * x1  # y intercept
        return abs(py - (a * px + b)) < TOLERANCE
    return False


def closest_point_on_line(line, point):
    x1, y1, x2, y2 = line
    px, py = point

    a = y2 - y1
    b = x1 - x2
    c1 = a * x1 + b * y1
    c2 = -b * px + a * py
    det = a * a - -b * b

    if det != 0:
        cx = a * c1 - b * c2 / det
        cy = a * c2 - -b * c1 / det
        return (cx, cy)
    else:
        return (px, py)


def line_line_intercept(line_a, line_b):
    x1, y1, x2, y2 = line_a
    x3, y3, x4, y4 = line_b

    a1 = y2 - y1
    b1 = x1 - x2
    c1 = a1 * x1 + b1 * y1
    a2 = y4 - y3
    b2 = x3 - x4
    c2 = a2 * x3 + b2 * y3

    det = a1 * b2 - a2 * b1

    if det != 0:
        x = (b2 * c1 - b1 * c2) / det
        y = (a1 * c2 - a2 * c1) / det
        if min(x1, x2) <= x <= max(x1, x2) and \
           min(x3, x4) <= x <= max(x3, x4) and \
           min(y1, y2) <= y <= max(y1, y2) and \
           min(y3, y4) <= y <= max(y3, y4):
            return (x, y)
    return None


def point_point(point_a, point_b):
    ax, ay = point_a
    bx, by = point_b
    return ax == bx and ay == by


def rect_circle(rect, circle):
    """Check if rectangle and circle are overlapping

    Args:
        rect (peachy.geo.Rect, tuple[x, y, w, h]): The rectangle to use in this
            collision detection procedure.
        circle (peachy.geo.Circle, tuple[x, y, r]): The circle to use in this
            collision detection procdure. Represented using a Circle or tuple.

    Note:
        This procedure will still run if arguments are reversed.
    """
    try:
        rect_x, rect_y, rect_width, rect_height = rect
        circle_x, circle_y, radius = circle
    except TypeError:
        rect_x, rect_y, rect_width, rect_height = circle
        circle_x, circle_y, radius = rect

    rect_x = rect_x + rect_width / 2
    rect_y = rect_y + rect_height / 2

    circle_x += radius
    circle_y += radius

    dist_x = abs(circle_x - rect_x)
    dist_y = abs(circle_y - rect_y)
    half_width = rect_width / 2
    half_height = rect_height / 2

    if dist_x > (half_width + radius) or \
       dist_y > (half_height + radius):
        return False

    if dist_x <= half_width or \
       dist_y <= half_height:
        return True

    corner_distance = (dist_x - half_width)**2 + (dist_y - half_height)**2

    return corner_distance <= (radius**2)


def rect_line(rect, line):
    x1, y1, x2, y2 = line
    rx, ry, rwidth, rheight = rect
    rr = rx + rwidth
    rb = ry + rheight

    if rect_point(rect, (x1, y1)) and rect_point(rect, (x2, y2)):
        return True  # line inside of rect
    elif (max(x1, x2) < rx or min(x1, x2) > rr or
         max(y1, y2) < ry or min(y1, y2) > rb):
        return False  # line outside of rect
    else:
        # line possibly intersecting rect
        segments = rect_to_vector_segments(rect)
        for segment in segments:
            rect_line = (segment[0], segment[1],
                         segment[0] + segment[2], segment[1] + segment[3])
            if line_line(line, rect_line):
                return True
    return False


def rect_point(rect, point):
    """Check if rectangle contains point.

    Args:
        point (peachy.geo.Point, tuple[x, y]): A point. Represented by
            either peachy.geo.Point or a tuple.
    """
    try:
        rect_x, rect_y, rect_width, rect_height = rect
        px, py = point
    except TypeError:
        rect_x, rect_y, rect_width, rect_height = point
        px, py = rect

    if rect_x <= px <= rect_x + rect_width and \
       rect_y <= py <= rect_y + rect_height:
        return True
    else:
        return False


def rect_rect(rect_a, rect_b):
    """Check if rectangle is colliding with another rectangle.

    Args:
        rect_a (peachy.Rect): The first rectangle candidate.
        rect_a (peachy.Rect): The second rectangle candidate.

    Returns:
        bool: True, if rectangles are overlapping.

    Raises:
        AttributeError: The object provided was invalid.
    """
    ax, ay, awidth, aheight = rect_a
    bx, by, bwidth, bheight = rect_b

    right_a = ax + awidth
    bottom_a = ay + aheight
    right_b = bx + bwidth
    bottom_b = by + bheight

    return (ax < right_b and right_a > bx and
            ay < bottom_b and bottom_a > by)
