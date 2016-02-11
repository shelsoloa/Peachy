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

def get_sound(asset_name):
    return Storage.sounds.get(asset_name)

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


