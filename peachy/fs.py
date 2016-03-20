import os
import pickle
import pygame

from peachy import DEBUG

resources = dict()


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
    return resources.get(asset_name)
    # TODO add troubleshooting 

def load_image(asset_name, path, store=True):
    """ Retrieves an image from the HDD """
    # path = path.lstrip('../')  # cannot rise outside of asset_path

    try:
        assert os.path.isfile(path)

        image = pygame.image.load(path)
        image.convert_alpha()
        if store:
            global resources
            resources[asset_name] = image
        return image

    except AssertionError:
        DEBUG('Image not found: ' + path)
        raise IOError('Image not found: ' + path)

    except pygame.error:
        DEBUG('Error loading image: ' + path)
        raise

def load_font(asset_name, path, point_size, store=True):
    """ Retrieves a font from the HDD """

    path = path.lstrip('../')  # cannot rise outside of asset_path

    try:
        font = pygame.font.Font(path, point_size)
        if store:
            global resources
            resources[asset_name] = font
        return font

    except IOError:
        # TODO incorporate default font
        DEBUG('Error loading font: ' + path)
        raise

def load_sound(asset_name, path, store=True):
    """ Retrieves a sound file from the HDD """
    # TODO add linux support

    path = path.lstrip('../')  # cannot rise outside of asset_path

    try:
        sound = pygame.mixer.Sound(path)
        if store:
            Storage.sounds[asset_name] = sound
        return sound
    except IOError:
        print '[ERROR] could not find Sound: ' + path
        return None


