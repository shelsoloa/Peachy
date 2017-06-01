# Collision functions are alphabetical but prioritze rectangles because
# they are most common


class CollisionResult(object):
    def __init__(self, f, a, b):
        self.collision_function = f
        self.shape_a = a
        self.shape_b = b


def collides_any(target_shape, testing_shapes):
    for shape in testing_shapes:
        result = collides_unknown(target_shape, shape)
        if result:
            return result
    return False


def collides_group(container, main_shape, group, collision_function=None):
    """Check if colliding with group.

    Check if self is colliding with any entity that is a member of the
    specified group.

    Args:
        group (str): The name of the group to survey.
        x (int, optional): Temporary replacement x coordinate for self.
        y (int. optional): Temporary replacement y coordinate for self.

    Returns:
        list[peachy.collision.CollisionResult]: A list of CollisionResults
            containing the colliding entities and the function used to detect
            collision.
    """

    collisions = []
    shapes = container.get_group(group)
    if len(shapes) > 0:
        if collision_function is None:
            collision = get_collision_function(main_shape, shapes[0])
        else:
            collision = collision_function

        for test in shapes:
            if collision(main_shape, test):
                collisions.append(CollisionResult(collision, main_shape, test))

    return collisions


def collides_groups(container, main_shape, groups, collision_function=None):
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


def collides_multiple(target_shape, test_shapes):
    collisions = []
    for shape in test_shapes:
        if collides_unknown(target_shape, shape):
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


def get_collision_function(shape_a, shape_b):
    from peachy.geo import CIRCLE_ID, LINE_ID, POINT_ID, RECT_ID

    collision_function = None

    if shape_a.type_int > shape_b.type_int:
        shape_a, shape_b = shape_b, shape_a

    if shape_a.typeid == RECT_ID:
        if shape_b.typeid == RECT_ID:
            collision_function = rect_rect
        elif shape_b.typeid == CIRCLE_ID:
            collision_function = rect_circle
        # elif shape_b.typeid == LINE_ID:
        #    collision_function = rect_line
        elif shape_b.typeid == POINT_ID:
            collision_function = rect_point
    elif shape_a.typeid == CIRCLE_ID:
        if shape_b.typeid == RECT_ID:
            collision_function = rect_circle
        elif shape_b.typeid == CIRCLE_ID:
            collision_function = circle_circle
        # elif shape_b.typeid == LINE_ID:
        #     collision_function = circle_line
        elif shape_b.typeid == POINT_ID:
            collision_function = circle_point
    elif shape_a.typeid == LINE_ID:
        # if shape_b.typeid == RECT_ID:
        #     collision_function = rect_line
        # elif shape_b.typeid == CIRCLE_ID:
        #     collision_function = circle_line
        if shape_b.typeid == LINE_ID:
            collision_function = line_line
        # elif shape_b.typeid == POINT_ID:
        #     collision_function = line_point
    elif shape_a.typeid == POINT_ID:
        if shape_b.typeid == RECT_ID:
            collision_function = rect_point
        elif shape_b.typeid == CIRCLE_ID:
            collision_function = circle_point
        # elif shape_b.typeid == POINT_ID:
        #     collision_function = point_point
        # elif shape_b.typeid == LINE_ID:
        #     collision_function = line_point
    # elif shape_a.typeid == POLYGON_ID:
    #     pass

    return collision_function


def circle_circle(circle_a, circle_b):
    ax, ay, ar = circle_a
    bx, by, br = circle_b

    ax += ar
    ay += ar
    bx += br
    by += br

    return (ax - bx)**2 + (ay - by)**2 <= (ar + br)**2


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

