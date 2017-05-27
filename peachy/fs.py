"""Peachy filesystem module

Multiple utilities for quickly and easily loading and saving files. Including:
raw objects, images, sounds, and a few others.
"""

import logging
import os
import pickle
import pygame
import xml.dom.minidom

import peachy
import peachy.audio
import peachy.graphics
from peachy.utils import Resource

resources = None
__resource_directory = None


def resource_directory(directory=None):
    """Get/Set resource directory

    Args:
        directory (str, optional): An absolute path that will prepend all
            resources requests made through peachy.fs

    Returns:
        str: The new resource directory. If directory is not specified or does
            not exist: no change takes place and function returns the previous
            resource_directory.

    Note:
        Can be set in PeachyConfiguration
    """
    global __resource_directory
    if directory is not None:
        try:
            assert os.path.exists(directory)
            __resource_directory = directory
        except AssertionError:
            logging.error('Asset directory must exist')
    return __resource_directory


def use_resource_directory(path):
    """Prepend the resource directory to the specified path

    Example:
        >>> resource_directory('/home/peachy/resources')
        >>> path = 'example.png'
        >>> path = use_resource_directory(path)
        >>> print(path)
        /home/peachy/resources/example.png

    Args:
        path (str): The path to append to resource directory.
    """
    if __resource_directory is not None:
        return os.path.join(__resource_directory, path)
    else:
        return path


def set_resource_manager(resource_manager, clear=False):
    """Change the current resource manager (peachy.fs.resources)

    Args:
        resource_manager (peachy.utils.ResourceManager): The new resource
            manager to use.
        clear (bool, optional): Should resources be cleared before changing to
            the new manager. Default is False.
    """
    global resources
    resources = resource_manager


def resource_loader(f):
    """Decorator for resource loading functions.

    Attempts to find resource inside resources dict before loading from
    filesystem. Also verifies whether resource exists or not.

    Args:
        resource_name (str): the name to store the resource under.
        resource_path (str): the path to the resource file.

    Raises:
        IOError: Resource was not found.
    """
    def load_from_resources(resource_name, resource_path, *args, **kwargs):
        # Attempt to load resource from resources(resource manager).
        resource = resources.get(resource_name)
        if resource:
            return resource.data

        resource_path = use_resource_directory(resource_path)

        try:
            assert os.path.isfile(resource_path)
        except AssertionError:
            logging.error("File not found: " + resource_path)
            raise IOError("File not found: " + resource_path)

        return f(resource_name, resource_path, *args, **kwargs)
    return load_from_resources


def open_xml(path):
    """Retrieve an xml file from the hard drive.

    Args:
        path (str): An absolute path to the requested xml file.

    Returns:
        xml.dom.minidom: A parsed xml minidom object.
    """
    try:
        xml_file = open(path, 'r')
        data = xml_file.read()
        xml_file.close()
        return xml.dom.minidom.parseString(data)
    except IOError:
        logging.error('Could not load xml file: ' + path)


def save_raw_data(data, file_name):
    """Save an object to a file.

    Args:
        data (object): The data to be saved.
        file_name (str): Where the data will be saved.

    Raises:
        IOError
        pickle.PickleError
    """
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
    """Load a previously pickled file into a variable and return it.

    Args:
        file_name (str): The absolute path to the requested file.

    Returns:
        object: The contents of the file.

    Raises:
        IOError
        pickle.PickleError
    """
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


def get_image(resource_name):
    """Retrieve an image from resources OR load from storage.

    Args:
        resource_name (str): The name the asset was registered under. If no
            asset is registered under resource_name, get_image will try using
            resource_name as a path to an image.

    Raises:
        pygame.error: If image is not found.
    """

    image = resources.get(resource_name)
    if image is None:
        return load_image('', resource_name, False)
    else:
        return image.resource


def get_font(resource_name, pt_size=-1):
    """Retrieve a font from resources OR load from storage.

    Args:
        resource_name (str): The name the asset was registered under. If no
            asset is registered under resource_name, get_image will try using
            resource_name as a path to an image.
        pt_size (int): The size of the font. Only used when loading.

    Raises:
        pygame.error: If font is not found.

    Todo:
        Store only one font per family and set point size in Font class or
        graphics.
    """

    font = resources.get(resource_name)
    if font is None and pt_size > 0:
        return load_font('', resource_name, pt_size, False)
    else:
        return font.resource


def get_sound(resource_name):
    """Retrieve a sound from resources OR load from storage.

    Args:
        resource_name (str): The name the asset was registered under. If no
            asset is registered under resource_name, get_image will try using
            resource_name as a path to an image.

    Raises:
        pygame.error: If sound is not found.
    """

    sound = resources.get(resource_name)
    if sound is None:
        return load_sound('', resource_name, False)
    else:
        return sound.resource


@resource_loader
def load_image(resource_name, resource_path, store=True):
    """Retrieve an image from the hard drive.

    Args:
        resource_name (str): The name to register the resource under.
        resource_path (str): The absolute path to the resource file.
        store (bool, optional): Whether the asset should be stored inside
            peachy.fs.resources.

    Raises:
        pygame.error: Could not load asset.
    """

    try:
        image = pygame.image.load(resource_path)
        image.convert_alpha()
        if store:
            if resource_name in resources:
                logging.warning('Resource %s overriden by %s' %
                                (resource_name, resource_path))

            resource = Resource(resource_name, resource_path,
                                resource=image, category='image')
            resources.add(resource)
        return image

    except pygame.error:
        logging.error('Loading image: ' + resource_path)
        raise


@resource_loader
def load_font(resource_name, resource_path, point_size, store=True):
    """Retrieve a font from the hard drive.

    Args:
        resource_name (str): The name to register the resource under.
        resource_path (str): The absolute path to the resource file.
        point_size (int): The size of font to use. 12pt, 24pt, etc.
        store (bool, optional): Whether the asset should be stored inside
            peachy.fs.resources.

    Raises:
        pygame.error: Could not load asset.
    """

    try:
        font = peachy.graphics.Font(resource_path, point_size)
        if store:
            if resource_name in resources:
                logging.warning('Resource %s overriden by %s' %
                                (resource_name, resource_path))

            resource = Resource(resource_name, resource_path,
                                resource=font, category='font')
            resources.add(resource)
        return font

    except pygame.error:
        logging.error('Loading font: ' + resource_path)


@resource_loader
def load_sound(resource_name, resource_path, store=True):
    """Retrieve a sound file from the hard drive.

    Args:
        resource_name (str): The name to register the resource under.
        resource_path (str): The absolute path to the resource file.
        store (bool, optional): Whether the asset should be stored inside
            peachy.fs.resources.

    Raises:
        pygame.error: Could not load asset.
    """

    try:
        sound = peachy.audio.Sound(resource_path)
        if store:
            if resource_name in resources:
                logging.warning('Resource %s overriden by %s' %
                                (resource_name, resource_path))
            resource = Resource(resource_name, resource_path,
                                resource=sound, category='sound')
            resources.add(resource)
        return sound

    except pygame.error:
        print('[ERROR] loading sound: ' + resource_path)
        return None
