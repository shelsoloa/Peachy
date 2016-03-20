import os
import pickle
import pygame

from peachy import DEBUG

# TODO store every resource with a reference to filename/path
resources = dict()

def resource_loader(f):
    """ Decorator for resource loading functions """
    def inner(asset_name, path, *args, **kwargs):
        global resources
        if asset_name in resources:
            DEBUG("Resource {{{0}}} is already loaded".format(asset_name))
            return resources[asset_name]
        
        try:
            assert os.path.isfile(path)
        except AssertionError:
            DEBUG("File not found: " + path)
            raise IOError("File not found: " + path)

        return f(asset_name, path, *args, **kwargs)
    return inner


def save_raw_data(data, file_name):
    _file = None
    try:
        _file = open(file_name, 'wb')
        pickle.dump(data, _file)
        _file.close()
    except (IOError, pickle.PickleError):
        if _file is not None:
            _file.close()
        raise

def load_raw_data(file_name):
    _file = None
    saved_data = None
    try:
        _file = open(file_name, 'rb')
        saved_data = pickle.load(_file)
        _file.close()
    except (IOError, pickle.PickleError):
        if _file is not None:
            _file.close()
        raise
    return saved_data

def get_image(asset_name):
    image = resources.get(asset_name)
    if image is None:
        return load_image('', asset_name, False)
    else:
        return image

def get_font(asset_name):
    font = resources.get(asset_name)
    if font is None:
        return load_font('', asset_name, False)
    else:
        return font

def get_sound(asset_name):
    sound = resources.get(asset_name)
    if sound is None:
        return load_sound('', asset_name, False)
    else:
        return font


@resource_loader
def load_image(asset_name, path, store=True):
    """ Retrieves an image from the HDD """
    try:
        image = pygame.image.load(path)
        image.convert_alpha()
        if store:
            resources[asset_name] = image
        return image

    except pygame.error:
        DEBUG('Error loading image: ' + path)
        raise

@resource_loader
def load_font(asset_name, path, point_size, store=True):
    """ Retrieves a font from the HDD """
    try:
        font = pygame.freetype.Font(path, point_size)
        if store:
            global resources
            resources[asset_name] = font
        return font

    except pygame.error:
        # TODO incorporate default font
        DEBUG('Error loading font: ' + path)
        raise

@resource_loader
def load_sound(asset_name, path, store=True):
    """ Retrieves a sound file from the HDD """
    # TODO add linux support

    path = path.lstrip('../')  # cannot rise outside of asset_path

    try:
        sound = pygame.mixer.Sound(path)
        if store:
            Storage.sounds[asset_name] = sound
        return sound

    except pygame.error:
        print('[ERROR] could not find Sound: ' + path)
        return None


