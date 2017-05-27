"""Peachy configuration module.

Loading configuration:
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

    """BACKEND used for rendering

    A future goal for peachy. Allow for different rendering backends to be used
    instead of pygame.
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

    Note: not fully implemented, currently we use FRAMES_PER_SECOND for both.
    """
    FRAMES_PER_SECOND = 60
    UPDATES_PER_SECOND = 60

    """VARIABLE_TIMESTEP & MAX_FRAMESKIP (not yet implemented)"""
    VARIABLE_TIMESTEP = False
    MAX_FRAMESKIP = -1

    """Title that will be displayed in window caption."""
    TITLE = 'Game'

    """Directory that resources are loaded from by default"""
    RESOURCE_DIRECTORY = 'resources'

    """Resource management class to be used.
    Defaults to peachy.utils.ResourceManager
    """
    RESOURCE_MANAGER = None

    """Width and height of rendering surface"""
    VIEW_WIDTH = 100
    VIEW_HEIGHT = 100

    """Multiplier to scale the screen by. Will increase window size."""
    VIEW_SCALE = 1

    def from_module(self):
        return

    def from_json(self):
        return
