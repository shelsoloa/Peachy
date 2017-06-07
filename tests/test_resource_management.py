import os
import peachy
import peachy.resources


rm = None


def test_start():
    global rm
    engine = peachy.Engine()
    engine.add_world(peachy.World('Test'))
    rm = peachy.resources.ResourceManager()


def test_add_remove():
    res = peachy.resources.Resource('test', None)
    rm.add_resource(res)

    assert res in rm
    assert 'test' in rm
    assert rm.get_resource('test') is res

    rm.remove_resource('test')
    assert res not in rm
    assert 'test' not in rm
    assert rm.get_resource('test') is None

    assert len(rm) == 0


def test_groups():
    res_a = peachy.resources.Resource('test_a', None)
    res_a.group = 'a c'
    res_b = peachy.resources.Resource('test_b', None)
    res_b.group = 'a'
    res_c = peachy.resources.Resource('test_c', None)
    res_c.group = 'a c'

    rm.add_resource(res_a)
    rm.add_resource(res_b)
    rm.add_resource(res_c)

    assert len(rm.get_group('a')) == 3
    assert len(rm.get_group('c')) == 2
    rm.remove_group('c')
    assert len(rm.get_group('a')) == 1
    rm.remove_group('a')
    assert len(rm.get_group('a')) == 0
    assert len(rm) == 0


def test_outline_bundle():
    RESOURCE_OUTLINE = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'res/test_outline.json')

    rm = peachy.resources.ResourceManager()
    rm.bind_outline(RESOURCE_OUTLINE)
    assert rm.outline is not None
    assert len(rm.resources) == 0
    assert len(rm.bundles) == 0

    rm.activate_bundle('test_bundle')
    assert len(rm.resources) == 1
    assert len(rm.bundles) == 1

    rm.deactivate_bundle('test_bundle')
    assert len(rm.resources) == 0
    assert len(rm.bundles) == 0

    rm.clear()
    assert rm.outline is None


def test_shutdown():
    peachy.PC().quit()
    peachy.PC().run()
