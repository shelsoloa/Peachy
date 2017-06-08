import peachy
import os
from peachy.stage import load_tiled_tmx

RESOURCE_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'res')


def test_load():
    print(RESOURCE_DIRECTORY)
    engine = peachy.Engine()
    engine.add_world(peachy.World('TestWorld'))
    load_tiled_tmx(os.path.join(RESOURCE_DIRECTORY, 'tmx1.tmx'))
    load_tiled_tmx(os.path.join(RESOURCE_DIRECTORY, 'tmx2.tmx'))
    engine.quit()
    engine.run()
