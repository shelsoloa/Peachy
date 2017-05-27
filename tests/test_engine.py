import peachy
import time

engine = None


def test_startup():
    global engine
    engine = peachy.Engine()
    engine.add_world(peachy.World('TestWorld'))


def test_resize():
    engine.resize(300, 300)
    assert engine.canvas_width == 300 and engine.canvas_height == 300
    time.sleep(0.25)

    engine.canvas_width = 320
    assert engine.canvas_width == 320
    time.sleep(0.25)

    engine.canvas_height = 240
    assert engine.canvas_height == 240
    time.sleep(0.25)


def test_fullscreen():
    # TODO, this function crashes pytest on Linux... Why?
    engine.toggle_fullscreen()
    engine.toggle_fullscreen()


def test_shutdown():
    print('shutdown')
    engine.quit()
    engine.run()
