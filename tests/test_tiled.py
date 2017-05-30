import peachy
from peachy.stage import load_tiled_tmx


def test_load():
    engine = peachy.Engine()
    engine.add_world(peachy.World('TestWorld'))
    load_tiled_tmx('tmx1.tmx')
    load_tiled_tmx('tmx2.tmx')
    engine.quit()
    engine.run()
