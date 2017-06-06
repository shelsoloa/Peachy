import os
import peachy
import peachy.fs


basedir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res')


def test_setup():
    print(basedir)
    peachy.Engine()


def test_load_image():
    image_tests = ['test_bmp.bmp', 'test_jpg.jpg', 'test_png.png',
                   'test_gif.gif']
    for test in image_tests:
        img = peachy.fs.load_image(os.path.join(basedir, test))
        assert isinstance(img, peachy.graphics.Surface)


def test_load_font():
    font_tests = ['test_otf.otf', 'test_ttf.ttf']
    for test in font_tests:
        f = peachy.fs.load_font(os.path.join(basedir, test), 12)
        assert f is not None
        assert isinstance(f, peachy.graphics.Font)


def test_load_sound():
    # TODO test mp3 support (currently limited by pygame)
    sound_tests = ['test_wav.wav', 'test_ogg.ogg']
    for test in sound_tests:
        sound = peachy.fs.load_sound(os.path.join(basedir, test))
        assert isinstance(sound, peachy.audio.Sound)


def test_cleanup():
    try:
        peachy.PC().force_shutdown()
    except SystemExit:
        pass
