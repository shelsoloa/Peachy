import os
import pygame

'''class Assets(object):
    """
    An asset management helper class
    """
'''

class Storage:
    fonts = dict()
    images = dict()
    sounds = dict()

def get_font(asset_name):
    return Storage.fonts.get(asset_name)

def get_image(asset_name):
    image = Storage.images.get(asset_name)
    if image is None:
        return load_image('', asset_name, False)
    else:
        return image

def get_sound(asset_name):
    return Storage.sounds.get(asset_name)

def load_font(asset_name, path, point_size, store=True):
    """Retrieves a font from the HDD"""

    path = path.lstrip('../')  # cannot rise outside of asset_path

    try:
        font = pygame.font.Font(path, point_size)
        if store:
            Storage.fonts[asset_name] = font
        return font
    except IOError:
        # TODO incorporate default font
        print '[ERROR] could not find Font: ' + path
        return None

def load_image(asset_name, path, store=True):
    """Retrieves an image from the HDD"""
    # path = path.lstrip('../')  # cannot rise outside of asset_path

    try:
        image = pygame.image.load(path)
        image.convert_alpha()
        if store:
            Storage.images[asset_name] = image
        return image
    except IOError:
        print '[ERROR] could not find Image: ' + path
        return None
    except pygame.error:
        print '[ERROR] could not load Image: ' + path
        return None

def load_sound(asset_name, path, store=True):
    """Retrieves a sound file from the HDD"""
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


