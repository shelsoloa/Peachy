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


# def collision_rect_circle(rect, circle):
#     """Check if rectangle is colliding with a circle
#
#     Args:
#         circle (peachy.geo.Circle, tuple[x, y, r]): The circle to check for
#             collision. Represented using a Circle or tuple.
#         x (int, optional): Override for self.x.
#         y (int, optional): Override for self.y.
#     """
#     if x is None or y is None:
#         x = self.x
#         y = self.y
#
#     circle_x, circle_y, radius = circle
#     circle_x += radius
#     circle_y += radius
#
#     rx = x + self.width / 2
#     ry = y + self.height / 2
#
#     dist_x = abs(circle_x - rx)
#     dist_y = abs(circle_y - ry)
#     half_width = self.width / 2
#     half_height = self.height / 2
#
#     if dist_x > (half_width + radius) or \
#        dist_y > (half_height + radius):
#         return False
#
#     if dist_x <= half_width or \
#        dist_y <= half_height:
#         return True
#
#     corner_distance = (dist_x - half_width)**2 + (dist_y - half_height)**2
#
#     return corner_distance <= (radius**2)
#
#
#
#
# def collides_point(self, point, x=None, y=None):
#     """Check if 'self' is colliding with a point.
#
#     Args:
#         point (peachy.geo.Point, tuple[x, y]): The point represented by
#             either a peachy Point or a tuple.
#         x (int, optional): Override for self.x
#         y (int, optional): Override for self.y
#     """
#     if x is None or y is None:
#         x = self.x
#         y = self.y
#
#     px, py = point
#     if x <= px <= x + self.width and y <= py <= y + self.height:
#         return True
#     else:
#         return False
#
#
# def collides_rect(self, rect, x=None, y=None):
#     """Check if 'self' is colliding with a rectangle.
#
#     Args:
#         rect (peachy.geo.Rect, tuple[x, y, width, height]): The rectangle
#             represented by either a peachy Point or tuple.
#         x (int, optional): Override for self.x
#         y (int, optional): Override for self.y
#     """
#     if x is None or y is None:
#         x = self.x
#         y = self.y
#
#     rx, ry, rwidth, rheight = rect
#
#     left_a = x
#     right_a = x + self.width
#     top_a = y
#     bottom_a = y + self.height
#
#     left_b = rx
#     right_b = rx + rwidth
#     top_b = ry
#     bottom_b = ry + rheight
#
#     if (bottom_a <= top_b or top_a >= bottom_b or
#             right_a <= left_b or left_a >= right_b):
#         return False
#     else:
#         return True
#
#
# def collides_groups(self, groups, x=None, y=None):
#     """Check if colliding with groups.
#
#     Check if self is colliding with any entity that is a member of ANY
#     of the groups specified.
#
#     Args:
#         groups (list[str]): A string list of group names to survey.
#         x (int, optional): Temporary replacement x coordinate for self.
#         y (int. optional): Temporary replacement y coordinate for self.
#
#     Returns:
#         list[peachy.Entity]: Every entity colliding with self that is a
#             member of any of the specified groups.
#     """
#
#     if x is None:
#         x = self.x
#     if y is None:
#         y = self.y
#
#     collisions = []
#     for entity in self.container.get_group(*groups):
#         if entity.active and self.collides(entity, x, y):
#             collisions.append(entity)
#     return collisions
#
#
# def collides_name(self, name, x=None, y=None):
#     """Check if colliding with named entity.
#
#     Args:
#         name (str): The name of the entity to check
#         x (int, optional): Temporary replacement x coordinate for self.
#         y (int. optional): Temporary replacement y coordinate for self.
#
#     Returns:
#         peachy.Entity: Returns entity if colliding or None if no collision.
#     """
#     if x is None or y is None:
#         x = self.x
#         y = self.y
#
#     entity = self.container.get_name(name)
#     if entity and self.collides(entity, x, y):
#         return entity
#     return None
#
#
# def collides_solid(self, x=None, y=None):
#     """Check if colliding with any solid entity.
#
#     Checks if self collides with any entity that has Entity.solid set as
#     True.
#
#     Args:
#         x (int, optional): Temporary replacement x coordinate for self.
#         y (int. optional): Temporary replacement y coordinate for self.
#
#     Returns:
#         list[peachy.Entity]: Every solid entity colliding with self.
#     """
#     if x is None or y is None:
#         x = self.x
#         y = self.y
#
#     collisions = []
#     for entity in self.container:
#         if entity is not self and entity.active and entity.solid and \
#            self.collides(entity, x, y):
#             collisions.append(entity)
#     return collisions


# def collides_group(self, group, x=None, y=None):
#     """Check if colliding with group.
#
#     Check if self is colliding with any entity that is a member of the
#     specified group.
#
#     Args:
#         group (str): The name of the group to survey.
#         x (int, optional): Temporary replacement x coordinate for self.
#         y (int. optional): Temporary replacement y coordinate for self.
#
#     Returns:
#         list[peachy.Entity]: Every entity of group colliding with self.
#     """
#
#     if x is None:
#         x = self.x
#     if y is None:
#         y = self.y
#
#     collisions = []
#     for entity in self.container.get_group(group):
#         if entity is not self and entity.active and \
#            self.collides(entity, x, y):
#             collisions.append(entity)
#     return collisions
#
# def collides_groups(self, groups, x=None, y=None):
#     """Check if colliding with groups.
#
#     Check if self is colliding with any entity that is a member of ANY
#     of the groups specified.
#
#     Args:
#         groups (list[str]): A string list of group names to survey.
#         x (int, optional): Temporary replacement x coordinate for self.
#         y (int. optional): Temporary replacement y coordinate for self.
#
#     Returns:
#         list[peachy.Entity]: Every entity colliding with self that is a
#             member of any of the specified groups.
#     """
#
#     if x is None:
#         x = self.x
#     if y is None:
#         y = self.y
#
#     collisions = []
#     for entity in self.container.get_group(*groups):
#         if entity.active and self.collides(entity, x, y):
#             collisions.append(entity)
#     return collisions
#
# def collides_name(self, name, x=None, y=None):
#     """Check if colliding with named entity.
#
#     Args:
#         name (str): The name of the entity to check
#         x (int, optional): Temporary replacement x coordinate for self.
#         y (int. optional): Temporary replacement y coordinate for self.
#
#     Returns:
#         peachy.Entity: Returns entity if colliding or None if no collision.
#     """
#     if x is None or y is None:
#         x = self.x
#         y = self.y
#
#     entity = self.container.get_name(name)
#     if entity and self.collides(entity, x, y):
#         return entity
#     return None
#
# def collides_solid(self, x=None, y=None):
#     """Check if colliding with any solid entity.
#
#     Checks if self collides with any entity that has Entity.solid set as
#     True.
#
#     Args:
#         x (int, optional): Temporary replacement x coordinate for self.
#         y (int. optional): Temporary replacement y coordinate for self.
#
#     Returns:
#         list[peachy.Entity]: Every solid entity colliding with self.
#     """
#     if x is None or y is None:
#         x = self.x
#         y = self.y
#
#     collisions = []
#     for entity in self.container:
#         if entity is not self and entity.active and entity.solid and \
#            self.collides(entity, x, y):
#             collisions.append(entity)
#     return collisions
