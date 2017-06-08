"""Peachy configuration module.

Loading configuration:

    Engine.init_from_config()

    >>> engine.config.from_module('config')
    # OR
    >>> engine.config.from_file('config.json')
    # OR
    >>> engine.config = CustomConfig()
"""

FIXED_TIMESTEP = 0
VARIABLE_TIMESTEP = 1


class PeachyConfiguration(object):
    """Configuration.

    All fields are held within PC.config.

    Inspired by configuration handling in Flask.
    """

    """BACKEND library used for rendering

    A future goal for peachy. Allow for rendering using different libraries
    such as: PySDL, pyglet, etc. Currently only pygame is supported.
    """
    BACKEND = 'pygame'

    """Background color used to clear screen each frame."""
    BACKGROUND_COLOR = (0, 0, 0)

    """Activate DEBUG mode."""
    DEBUG = False

    """Default font to be loaded into peachy.graphics"""
    DEFAULT_FONT = ''  # TODO

    """Amount of render calls per second and amount of update calls per second,
    respectively.
    Note: not fully implemented, currently FRAMES_PER_SECOND is used for both.
    """
    FRAMES_PER_SECOND = 60
    UPDATES_PER_SECOND = 60

    """VARIABLE_TIMESTEP & MAX_FRAMESKIP (not yet implemented)"""
    VARIABLE_TIMESTEP = False
    MAX_FRAMESKIP = -1

    """Title that will be displayed in window caption."""
    TITLE = 'Game'

    """Path to resources.json"""
    RESOURCE_DIRECTORY = 'res'

    """Width and height of rendering surface"""
    VIEW_WIDTH = 100
    VIEW_HEIGHT = 100

    """Multiplier to scale the screen by. Will increase window size."""
    VIEW_SCALE = 1
