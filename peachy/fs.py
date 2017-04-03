import os
import pickle
import pygame
import xml.dom.minidom

import peachy

# TODO store every resource with a reference to filename/path
resources = dict()


def resource_loader(f):
    """ Decorator for resource loading functions """
    def inner(asset_name, path, *args, **kwargs):
        global resources
        if asset_name in resources:
            return resources[asset_name]

        try:
            assert os.path.isfile(path)
        except AssertionError:
            peachy.DEBUG("File not found: " + path)
            raise IOError("File not found: " + path)

        return f(asset_name, path, *args, **kwargs)
    return inner


def open_xml(path):
    """ Retrieve an xml file from the hard drive """
    try:
        xml_file = open(path, 'r')
        data = xml_file.read()
        xml_file.close()
        return xml.dom.minidom.parseString(data)
    except IOError:
        peachy.DEBUG('[ERROR] could not load xml file: ' + path)


def save_raw_data(data, file_name):
    """ Save data to a file """
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
    """ Return data from a file """
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
    """
    Retrieve an image from resources OR load from storage.

    If the image is not stored in resources then this function will attempt to
    find it using asset_name as path.

    If an image is not found, then a pygame.error is raised.
    """

    image = resources.get(asset_name)
    if image is None:
        return load_image('', asset_name, False)
    else:
        return image


def get_font(asset_name, pt_size=-1):
    """
    Retrieve a font from resources OR load from storage.

    If the font is not stored in resources then this function will attempt to
    find it using asset_name as path.

    If a font is not found, then a pygame.error is raised.
    """

    font = resources.get(asset_name)
    if font is None and pt_size > 0:
        return load_font('', asset_name, pt_size, False)
    else:
        return font


def get_sound(asset_name):
    """
    Retrieve a sound from resources OR load from storage.

    If the sound is not stored in resources then this function will attempt to
    find it using asset_name as path.

    If a sound is not found, then a pygame.error is raised.
    """

    sound = resources.get(asset_name)
    if sound is None:
        return load_sound('', asset_name, False)
    else:
        return sound


@resource_loader
def load_image(asset_name, path, store=True):
    """ Retrieve an image from the hard drive """
    try:
        image = pygame.image.load(path)
        image.convert_alpha()
        if store:
            if asset_name in resources:
                peachy.DEBUG('[WARN] resource %s is being overriden by %s' %
                             (asset_name, path))
            resources[asset_name] = image
        return image

    except pygame.error:
        peachy.DEBUG('[ERROR] loading image: ' + path)
        raise


@resource_loader
def load_font(asset_name, path, point_size, store=True):
    """ Retrieve a font from the hard drive """
    try:
        font = peachy.graphics.Font(path, point_size)
        if store:
            if asset_name in resources:
                peachy.DEBUG('[WARN] resource %s is being overriden by %s' %
                             (asset_name, path))
            resources[asset_name] = font
        return font

    except pygame.error:
        peachy.DEBUG('[ERROR] loading font: ' + path)
        raise


@resource_loader
def load_sound(asset_name, path, store=True):
    """ Retrieve a sound file from the hard drive """
    # TODO add linux support

    try:
        sound = peachy.audio.Sound(path)
        if store:
            if asset_name in resources:
                peachy.DEBUG('[WARN] resource %s is being overriden by %s' %
                             (asset_name, path))
            resources[asset_name] = sound
        return sound

    except pygame.error:
        print('[ERROR] loading sound: ' + path)
        return None
