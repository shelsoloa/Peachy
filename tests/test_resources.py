"""The get_function is the function used to get a resource of that type:

image -> get_image
sound -> get_sound
etc.
"""

import os
import peachy
import peachy.fs


def test_setup():
    engine = peachy.Engine()
    engine.add_world(peachy.World('Test'))


def test_resource_directory():
    target_path = os.path.join(os.path.realpath(os.getcwd()), 'tests', 'res')
    peachy.fs.resource_directory(target_path)
    assert peachy.fs.resource_directory() == target_path

    peachy.fs.resource_directory('fakedirectorypathname')
    assert peachy.fs.resource_directory() == target_path
    assert peachy.fs.use_resource_directory('test_png.png') == \
        os.path.join(target_path, 'test_png.png')


def test_add_resource():
    resource = peachy.fs.Resource('RES1', 'test_png.png')
    peachy.fs.resources.add(resource)
    # assert type(peachy.fs.resources.add(resource)) == peachy.fs.Resource
    assert resource in peachy.fs.resources


def test_get_resource():
    assert peachy.fs.resources.get('RES1') is not None
    assert type(peachy.fs.resources.get('RES1')) == peachy.fs.Resource


def test_remove_resource():
    assert type(peachy.fs.resources.remove('RES1')) == peachy.fs.Resource
    assert peachy.fs.resources.get('RES1') is None


def test_rename_resource():
    res = peachy.fs.Resource('RES1', 'test_png.png')
    peachy.fs.resources.add(res)
    assert peachy.fs.resources.get('RES1') is not None
    peachy.fs.resources.rename('RES1', 'RES2')
    assert peachy.fs.resources.get('RES2') is not None
    assert peachy.fs.resources.get('RES2') == res
    peachy.fs.resources.remove('RES2')
    assert peachy.fs.resources.get('RES2') is None


def test_categorize_resource():
    res1 = peachy.fs.Resource('RES1', 'test_png.png', category='res')
    res2 = peachy.fs.Resource('RES2', 'test_png.png', category='d')
    res3 = peachy.fs.Resource('RES3', 'test_png.png', category='res d')
    peachy.fs.resources.add(res1, res2, res3)
    assert len(peachy.fs.resources) == 3
    assert len(peachy.fs.resources.get_category('res')) == 2
    assert len(peachy.fs.resources.get_category('d')) == 2
    peachy.fs.resources.remove_category('d')
    assert len(peachy.fs.resources.get_category('res')) == 1


def test_clear_resources():
    peachy.fs.resources.add(peachy.fs.Resource('RES', 'test_png.png'))
    assert len(peachy.fs.resources) > 0
    peachy.fs.resources.clear()
    assert len(peachy.fs.resources) == 0


def test_image_operations():
    image_tests = ['test_bmp.bmp', 'test_jpg.jpg', 'test_png.png',
                   'test_gif.gif']
    for test in image_tests:
        _test_resource(
            'TEST_IMAGE', test,
            peachy.base.pygame.Surface,
            peachy.fs.get_image, peachy.fs.load_image
        )


def _test_font_operations():
    font_tests = ['test_font.otf', 'test_font.ttf']
    for test in font_tests:
        _test_resource(
            'TEST_FONT', test,
            peachy.base.pygame.freetype.Font,
            peachy.fs.get_font, peachy.fs.load_font
        )


def _test_sound_operations():
    sound_tests = ['test_sound.wav', 'test_sound.mp3', 'test_sound.ogg']
    for test in sound_tests:
        _test_resource(
            'TEST_SOUND', test,
            peachy.audio.Sound,
            peachy.fs.get_sound, peachy.fs.load_sound
        )


def test_cleanup():
    peachy.PC().quit()
    peachy.PC().run()
    assert len(peachy.fs.resources) == 0


def _test_resource(res_name, res_path, res_type, get_function, load_function):
    _load_resource(res_name, res_path, res_type, load_function)
    _get_resource(res_name, res_path, res_type, get_function)
    _remove_resource(res_name, res_path, get_function)
    _add_resource(res_path, res_type, load_function, get_function)
    peachy.fs.resources.clear()


def _add_resource(res_path, res_type, load_function, get_function):
    res = get_function(res_path)
    peachy.fs.resources.add(res)
    assert type(peachy.fs.resources.get(res)) == peachy.fs.Resource
    assert type(get_function(res)) == res_type


def _load_resource(res_name, res_path, res_type, load_function):
    assert type(load_function(res_name, res_path, store=False)) == res_type
    assert type(load_function(res_name, res_path)) == res_type


def _get_resource(res_name, res_path, res_type, get_function):
    assert type(peachy.fs.resources.get(res_name)) == peachy.fs.Resource
    assert type(peachy.fs.resources.get(res_path)) == peachy.fs.Resource
    assert type(peachy.fs.resources.get(res_name).res) == res_type
    assert type(get_function(res_name)) == res_type
    assert type(get_function(res_path)) == res_type
    res = get_function(res_name)
    assert type(peachy.PC.resources.get(res)) == peachy.fs.Resource


def _remove_resource(res_name, res_path, get_function):

    def assert_removal():
        assert peachy.fs.resources.get(res_name) is None
        assert peachy.fs.resources.get(res_path) is None
        assert peachy.fs.get_function(res_name) is None
        assert peachy.fs.get_function(res_path) is None

    resource = peachy.fs.resources.remove(res_name)
    assert_removal()

    peachy.fs.resources.add(resource)
    assert peachy.fs.resources.get(res_name) == resource
    assert peachy.fs.get_function(res_name) == resource
    peachy.fs.resources.remove(resource)
    assert_removal()
