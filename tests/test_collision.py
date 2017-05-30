import peachy
import peachy.collision
import peachy.geo

engine = None


def test_startup():
    global engine
    engine = peachy.Engine()
    engine.add_world(peachy.World('World'))


def test_rect_rect():
    rect_one = peachy.geo.Rect(0, 0, 100, 100)
    rect_two = peachy.geo.Rect(0, 0, 100, 100)
    assert peachy.collision.rect_rect(rect_one, rect_two)
    assert not peachy.collision.rect_rect(rect_one.temp_relocate(x=200),
                                          rect_two)
    assert not peachy.collision.rect_rect(rect_one,
                                          rect_two.temp_relocate(x=200))
    assert peachy.collision.rect_rect(rect_one.temp_relocate(x=200),
                                      rect_two.temp_relocate(x=200))
    assert not peachy.collision.rect_rect(rect_one.temp_relocate(y=200),
                                          rect_two)
    assert not peachy.collision.rect_rect(rect_one,
                                          rect_two.temp_relocate(y=200))
    assert peachy.collision.rect_rect(rect_one.temp_relocate(y=200),
                                      rect_two.temp_relocate(y=200))
    assert peachy.collision.rect_rect(rect_one.temp_relocate(200, 200),
                                      rect_two.temp_relocate(200, 200))


def test_cleanup():
    engine.shutdown()
