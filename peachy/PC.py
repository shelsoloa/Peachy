import pygame


class PC(object):
    """
    PC (Peachy Controller)
    This is the central access point for classes within the Peachy framework.
    This class contains references to the window, world, and entity room. Its
    values are set after startup.
    """

    fps = 0
    scale = -1
    title = ''

    background_color = (0, 0, 0)

    width = 0
    height = 0

    engine = None

    debug = False

    @property
    def world(self):
        return PC.engine.world

    @property
    def stage(self):
        return PC.engine.world.stage

    @staticmethod
    def quit():
        pygame.event.post(pygame.event.Event(pygame.locals.QUIT))
