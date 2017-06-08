import peachy
import peachy.collision
import peachy.geo


class CircleEntity(peachy.Entity, peachy.geo.Circle):
    def __init__(self, x, y, r):
        peachy.Entity.__init__(self)
        peachy.geo.Circle.__init__(self, x, y, r)


class LineEntity(peachy.Entity, peachy.geo.Line):
    def __init__(self, x1, y1, x2, y2):
        peachy.Entity.__init__(self)
        peachy.geo.Line.__init__(self, x1, y1, x2, y2)


class PointEntity(peachy.Entity, peachy.geo.Point):
    def __init__(self, x, y):
        peachy.Entity.__init__(self)
        peachy.geo.Point.__init__(self, x, y)


class RectEntity(peachy.Entity, peachy.geo.Rect):
    def __init__(self, x, y, width, height):
        peachy.Entity.__init__(self)
        peachy.geo.Rect.__init__(self, x, y, width, height)


def plot_lines():
    a = peachy.geo.Line(-7, 7, 15, 7)
    b = peachy.geo.Line(3, 8, 14, -3)
    c = peachy.geo.Line(11, 10, 5, 1)
    d = peachy.geo.Line(-1, -3, -1, 8)
    e = peachy.geo.Line(6, -3, 6, -6)
    f = peachy.geo.Line(-3, 0, 9, -6)

    return a, b, c, d, e, f


def test_rect_rect():
    rect_one = peachy.geo.Rect(0, 0, 100, 100)
    rect_two = peachy.geo.Rect(0, 0, 100, 100)
    collision = peachy.collision.rect_rect

    assert collision(rect_one, rect_two)
    assert not collision(rect_one.at_point(x=200), rect_two)
    assert not collision(rect_one, rect_two.at_point(x=200))
    assert collision(rect_one.at_point(x=200), rect_two.at_point(x=200))
    assert not collision(rect_one.at_point(y=200), rect_two)
    assert not collision(rect_one, rect_two.at_point(y=200))
    assert collision(rect_one.at_point(y=200), rect_two.at_point(y=200))
    assert collision(rect_one.at_point(200, 200), rect_two.at_point(200, 200))


def test_rect_circle():
    rect = peachy.geo.Rect(0, 0, 100, 100)
    circle = peachy.geo.Circle(0, 0, 50)
    collision = peachy.collision.rect_circle

    assert collision(rect, circle)
    assert not collision(rect.at_point(x=200), circle)
    assert not collision(rect, circle.at_point(x=101))
    assert collision(rect.at_point(x=200), circle.at_point(x=101))
    assert not collision(rect.at_point(y=200), circle)
    assert not collision(rect, circle.at_point(y=200))
    assert collision(rect.at_point(y=200), circle.at_point(y=200))
    assert collision(rect.at_point(200, 200), circle.at_point(200, 200))

    # >=14 is the closest a 50r circle at 45deg can be at without colliding
    assert not collision(rect, circle.at_point(86, 86))
    assert collision(rect, circle.at_point(85, 85))
    assert not collision(rect, circle.at_point(-86, 86))
    assert not collision(rect, circle.at_point(-86, -86))
    assert not collision(rect, circle.at_point(86, -86))


def test_rect_line():
    rect = peachy.geo.Rect(0, 0, 100, 100)
    collision = peachy.collision.rect_line

    assert collision(rect, (-10, 50, 50, 50))
    assert collision(rect, (25, 25, 75, 75))
    assert not collision(rect, (0, 110, 100, 110))
    assert not collision(rect, (-30, 10, -10, 200))


def test_rect_point():
    rect = peachy.geo.Rect(0, 0, 100, 100)
    collision = peachy.collision.rect_point

    assert collision(rect, (50, 50))
    assert not collision(rect, (101, 101))


def test_circle_circle():
    circle_a = peachy.geo.Circle(0, 0, 50)
    circle_b = peachy.geo.Circle(0, 0, 50)
    collision = peachy.collision.circle_circle

    assert collision(circle_a, circle_b)
    assert not collision(circle_a, circle_b.at_point(x=101))
    assert not collision(circle_a.at_point(y=101), circle_b)
    assert collision(circle_a.at_point(50, 50), circle_b.at_point(149, 50))
    assert not collision(circle_a, circle_b.at_point(x=75, y=75))


def test_circle_line():
    circle = peachy.geo.Circle(0, 0, 50)
    collision = peachy.collision.circle_line

    assert collision(circle, (-50, 50, 50, 50))
    assert not collision(circle.at_point(50, 50), (83, 87, 88, 82))


def test_circle_point():
    circle = peachy.geo.Circle(0, 0, 50)
    collision = peachy.collision.circle_point

    assert collision(circle, (50, 50))
    assert not collision(circle, (86, 86))
    assert collision(circle.at_point(50, 50), (100, 100))
    assert not collision(circle, (136, 136))


def test_line_line():
    a, b, c, d, e, f = plot_lines()
    collision = peachy.collision.line_line

    assert collision(a, b)
    assert collision(a, c)
    assert collision(a, d)
    assert collision(b, c)
    assert collision(d, f)
    assert collision(e, f)
    assert not collision(c, f)
    assert not collision(d, e)

    # line line intercepts
    assert peachy.collision.line_line_intercept(a, b) == (4, 7)
    assert peachy.collision.line_line_intercept(b, c) == (7, 4)
    assert peachy.collision.line_line_intercept(e, f) == (6, -4.5)
    assert peachy.collision.line_line_intercept(d, e) is None
    assert peachy.collision.line_line_intercept(c, f) is None


def test_line_point():
    a, b, c, d, e, f = plot_lines()
    collision = peachy.collision.line_point

    assert collision(a, (-6, 7))
    assert collision(b, (8, 3))
    assert collision(c, (9, 7))
    assert collision(d, (-1, 4))
    assert collision(e, (6, -3))
    assert collision(f, (1, -2))
    assert not collision(a, (-7, 6.5))
    assert not collision(b, (6, 4))


def test_point_point():
    collision = peachy.collision.point_point

    assert collision((0, 0), (0, 0))
    assert collision((256, 26), (256, 26))
    assert not collision((0, 0), (-1, 1))


def test_collides_multiple():
    room = peachy.Room(None)
    collision = peachy.collision.collides_multiple

    rect_entity = RectEntity(0, 0, 100, 100)
    room.add(rect_entity)
    room.add(CircleEntity(0, 0, 50))
    room.add(PointEntity(50, 50))
    room.add(LineEntity(-50, 50, 50, 50))

    assert len(collision(room, rect_entity)) == 3
    assert len(collision(room, RectEntity(200, 200, 50, 50))) == 0


def test_collide_name():
    room = peachy.Room(None)

    rect_entity = RectEntity(0, 0, 100, 100)
    circle_entity = CircleEntity(0, 0, 50)
    circle_entity.name = 'test'

    room.add(rect_entity)
    room.add(circle_entity)
    room.add(PointEntity(50, 50))
    room.add(LineEntity(-50, 50, 50, 50))

    assert peachy.collision.collides_name(room, rect_entity, 'test')


def test_collide_groups():
    room = peachy.Room(None)
    collision = peachy.collision.collides_group

    rect_entity = RectEntity(0, 0, 100, 100)
    circle_entity = CircleEntity(0, 0, 50)
    point_entity = PointEntity(50, 50)
    line_entity = LineEntity(-50, 50, 50, 50)
    rect_entity.group = 'group-a group-b'
    circle_entity.group = 'group-b'
    point_entity.group = 'group-b'

    room.add(rect_entity)
    room.add(circle_entity)
    room.add(point_entity)
    room.add(line_entity)

    assert len(collision(room, 'group-a', circle_entity)) == 1
    assert len(collision(room, 'group-b', line_entity)) == 3
    assert len(collision(room, 'group-a', rect_entity)) == 0
