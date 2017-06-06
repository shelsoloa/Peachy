"""Peachy filesystem module

Multiple utilities for quickly and easily loading and saving files. Including:
raw objects, images, sounds, and a few others.
"""

import logging
import pickle
import pygame
# import xml.dom.minidom

import peachy.audio
import peachy.graphics


# def open_xml(path):
#     """Retrieve an xml file from the hard drive.
#
#     Args:
#         path (str): An absolute path to the requested xml file.
#
#     Returns:
#         xml.dom.minidom: A parsed xml minidom object.
#     """
#     try:
#         xml_file = open(path, 'r')
#         data = xml_file.read()
#         xml_file.close()
#         return xml.dom.minidom.parseString(data)
#     except IOError:
#         logging.error('Could not load xml file: ' + path)


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


def load_image(resource_path):
    """Retrieve an image from the hard drive.

    Args:
        resource_path (str): The absolute path to the resource file.

    Raises:
        pygame.error: Could not load asset.
    """

    try:
        image = pygame.image.load(resource_path)
        image.convert_alpha()
        return image

    except pygame.error:
        logging.error('Loading image: ' + resource_path)
        raise


def load_font(resource_path, point_size):
    """Retrieve a font from the hard drive.

    Args:
        resource_path (str): The absolute path to the resource file.
        point_size (int): The size of font to use. 12pt, 24pt, etc.

    Raises:
        pygame.error: Could not load asset.
    """

    try:
        font = peachy.graphics.Font(resource_path, point_size)
        return font

    except pygame.error:
        logging.error('Loading font: ' + resource_path)


def load_sound(resource_path):
    """Retrieve a sound file from the hard drive.

    Args:
        resource_path (str): The absolute path to the resource file.
        store (bool, optional): Whether the asset should be stored inside
            peachy.fs.resources.

    Raises:
        pygame.error: Could not load asset.
    """

    try:
        sound = peachy.audio.Sound(resource_path)
        return sound

    except pygame.error:
        print('[ERROR] loading sound: ' + resource_path)
        return None
