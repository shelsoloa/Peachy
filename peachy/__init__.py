import math
import os
import platform
import sys

import pygame
from pygame.locals import *


def DEBUG(*objs):
    """ Print debug information to outstream (Only if DEBUG is active) """
    if PC.debug:
        print("[DEBUG]", *objs, file=sys.stderr)

def get_version():
    return '0.0.2'


class PC(object):
    """
    PC (Peachy Controller)
    This is the central access point for classes within the Peachy framework.
    This class contains references to the window, world, and entity room. Its
    values are set after startup.
    This is the only class that can be accessed by submodules within the Peachy
    framework.
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
        pygame.event.post(pygame.event.Event(QUIT))


import peachy.fs as fs
import peachy.graphics as graphics
import peachy.utils as utils
import peachy.audio as audio
import peachy.stage as stage


class Engine(object):
    """
    Engine is the main controller for Peachy and controls priority aspects of
    the applications such as: initializing the game, running the game loop,
    and controlling World objects.
    """

    def __init__(self, view_size, title='', fps=60, scale=1, debug=False,
                 resizable=False):
        self.worlds = {}
        self.world = None

        PC.engine = self
        PC.width = view_size[0]
        PC.height = view_size[1]
        PC.title = title
        PC.scale = scale
        PC.fps = fps
        PC.debug = debug

        self._render_surface = None
        self._window_surface = None

        plat = ''

        if fps <= 0:
            PC.fps = 60
        if debug:
            plat = platform.system()

        # Initialize pygame
        os.environ['SDL_VIDEO_CENTERED'] = "1"

        try:
            pygame.mixer.pre_init(44100, -16, 8, 512)
            pygame.display.init()
            pygame.freetype.init()
            pygame.mixer.init()
            # Joystick module prints useless dialog
            # pygame.joystick.init()
        except Exception:
            if pygame.display.get_init() is None:
                print("[ERROR] Could not initialize pygame display. Abort")
            elif pygame.font.get_init() is None:
                print("[ERROR] Could not initialize pygame font. About!")
            elif pygame.freetype.get_init() is None:
                print("[ERROR] Could not initialize pygame freetype. Abort!")
            elif pygame.mixer.get_init() is None:
                print("[ERROR] Could not initialize pygame mixer. Abort!")
            return -1

        # General initialization
        pygame.display.set_caption(title)
        utils.Keys.init()
        utils.Mouse.init()

        # Initialize display (pygame)
        self.view_size = (PC.width, PC.height)
        self.window_size = (PC.width * scale, PC.height * scale)

        flags = 0
        if resizable:
            flags += RESIZABLE

        self._window_surface = pygame.display.set_mode(self.window_size, flags)
        self._render_surface = pygame.Surface(self.view_size)

        graphics.DEFAULT_CONTEXT = self._render_surface
        graphics.set_context(self._render_surface)

        try:
            graphics.__font = graphics.Font('peachy/fonts/ProggyClean.ttf', 16)
        except IOError:
            utils.DEBUG("Debug font not found")
            # TODO exit

    def add_world(self, world, name=''):
        """
        Adds world to the Engine.worlds list. If there are no worlds in worlds
        list, then this worlds is set as active.

        Key for this world is name or world.name if name is left unspecified
        """

        if not name:
            name = world.name

        self.worlds[name] = world
        if self.world is None:
            self.world = world
            PC.world = self.world

        return self.worlds[name]

    def change_world(self, world_name):
        """
        Changes world to world specified. World must already be added through
        add_world().

        If no world is found, None is returned.
        """

        if world_name in self.worlds:
            self.world.exit()
            self.world = self.worlds[world_name]
            self.world.enter()
            return self.world
        else:
            DEBUG('World not found: {0}'.format(world))
            return None

    def get_world(self, world_name):
        return self.worlds.get(world_name)

    def set_title(self, title):
        PC.title = title
        pygame.display.set_caption(title)

    def fullscreen(self):
        """ Toggles fullscreen """
        screen = pygame.display.get_surface()
        caption = pygame.display.get_caption()

        flags = screen.get_flags()
        bits = screen.get_bitsize()

        pygame.display.quit()
        pygame.display.init()

        window_size = (0, 0)

        if flags^FULLSCREEN:
            monitor_info = pygame.display.Info()

            ratio = min(float(monitor_info.current_w) / float(PC.width),
                        float(monitor_info.current_h) / float(PC.height))

            window_width = int(PC.width * ratio)
            window_height = int(PC.height * ratio)
            self.window_size = (window_width, window_height)
        else:
            self.window_size = (PC.width * PC.scale, PC.height * PC.scale)

        pygame.display.set_caption(*caption)

        self._window_surface = pygame.display.set_mode(self.window_size, flags^FULLSCREEN, bits)
        # pygame.display.set_mode(window_size, flags^FULLSCREEN, bits)
        self._render_surface = pygame.Surface(self.view_size)

        graphics.DEFAULT_CONTEXT = self._render_surface
        graphics.set_context(self._render_surface)

    def preload(self):
        """
        Called at the beginning of run() before entering the main game loop.
        Used to load any startup resources or perform required operations.
        """
        return

    def resize(self, width, height):
        self.view_size = (width, height)
        screen = pygame.display.get_surface()
        flags = screen.get_flags()
        bits = screen.get_bitsize()
        self.window_size = (width * PC.scale, height * PC.scale)
        self._window_surface = pygame.display.set_mode(self.window_size, flags, bits)
        self._render_surface = pygame.Surface(self.view_size)
        graphics.DEFAULT_CONTEXT = self._render_surface
        graphics.set_context(self._render_surface)
        PC.width = width
        PC.height = height

    def run(self):
        """ Start game loop (calls preload before running game loop) """

        game_timer = pygame.time.Clock()
        utils.Mouse._poll()
        utils.Keys._poll()

        self.preload()
        self.world.enter()

        running = True
        try:  # a try to catch any missed exceptions
            while running:
                if self.world is not PC.world:
                    PC.world = self.world

                # Parse events
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                        break
                    elif event.type == VIDEORESIZE:
                        self.resize(event.w, event.h)

                utils.Mouse._poll()
                utils.Keys._poll()

                # Update
                self.world.update()

                # Render - Draw World
                self._render_surface.fill(PC.background_color)
                self.world.render()

                # Render - Transformations
                # TODO speed up scaling somehow
                pygame.transform.scale(self._render_surface, self.window_size, self._window_surface)

                # Render - Finalize
                pygame.display.flip()

                # Maintain fps (display if DEBUG is active)
                game_timer.tick(PC.fps)
                if PC.debug:
                    fps = round(game_timer.get_fps())
                    pygame.display.set_caption(PC.title + ' {' + str(fps) + '}')

            self.shutdown()  # Shutdown all peachy modules
            pygame.event.get()  # Throw away any pending events
            pygame.mixer.quit()
            pygame.quit()  # Shutdown all pygame modules

        except:
            import traceback
            print("[ERROR] Unexpected error. {0} shutting down.".format(PC.title))
            traceback.print_exc()
        sys.exit()

    def shutdown(self):
        """ Shutdown procedure called right before exiting Peachy """

        for _, world in self.worlds.items():
            world.shutdown()


class Entity(object):
    """
    Interactive game object
    """

    def __init__(self, x=0, y=0):
        self.group = ''           # Every entity belongs to a group
        self.name = ''            # Unique entities have a name (1/room)

        self.x = x                # x coordinate
        self.y = y                # y coordinate
        self.width = 0            # width (collision detection)
        self.height = 0           # height (collision detection)

        self.velocity_x = 0       # x-axis velocity
        self.velocity_y =  0      # y-axis velocity

        self.active = True        # If the entity is being updated
        self.visible = True       # If the entity is being rendered
        self.solid = False        # If the entity registers as a solid object (collision detection)

        self.sprite = None        # sprite used for rendering
        self.order = 0            # Used for sorting entity render order

        self.container = None     # The owner of this entity. Must be set before performing any operations involving groups of entities

    @property
    def group(self):
        return self.__groups

    @group.setter
    def group(self, groups):
        self.__groups = groups.split()

    def center(self):
        """ Return center coordinates of entity in a tuple """
        return (self.x + self.width / 2, self.y + self.height / 2)

    def destroy(self):
        """
        Remove entity from parent container and set as inactive. Note that
        resources will not be released until all references to this entity
        have been removed.
        """
        self.container.remove(self)
        self.active = False
        self.world = None

    def collides(self, e, x, y):
        """ Check if 'self' is colliding with specified entity 'e' """

        right_a = x + self.width
        bottom_a = y + self.height
        right_b = e.x + e.width
        bottom_b = e.y + e.height

        if x < right_b and \
           right_a > e.x and \
           y < bottom_b and \
           bottom_a > e.y:
            return True
        else:
            return False

    def collides_group(self, group, x=None, y=None):
        """
        Check if 'self' is colliding with any entity that is a member of the
        specificed group. Returns every colliding entity.
        Can provide custom x/y or leave blank for self.x/self.y.
        """

        if x is None or y is None:
            x = self.x
            y = self.y

        collisions = []
        entities = self.container.get_group(group)

        try:
            entities.remove(self)
        except ValueError:
            pass

        for entity in entities:
            if entity.active and self.collides(entity, x, y):
                collisions.append(entity)
        return collisions

    def collides_groups(self, x, y, *groups):
        """
        Check if 'self' is colliding with any entity that is a member of ANY
        of the groups specificed. Returns every colliding entity.
        """
        # TODO convert to *args
        if x is None or y is None:
            x = self.x
            y = self.y

        # receive possible entities
        entities = []
        for group in groups:
            entities += self.container.get_group(group)

        # remove duplicates
        keys = {}
        for e in entities:
            keys[e] = 1
        keys.pop(self, None)
        entities = keys.keys()

        # collision detection
        collisions = []
        for entity in entities:
            if entity.active and self.collides(entity, x, y):
                collisions.append(entity)
        return collisions

    def collides_name(self, name, x=None, y=None):
        """ Check if 'self' is colliding with entity of a specific name """
        if x is None or y is None:
            x = self.x
            y = self.y

        entity = self.container.get_name(name)
        if entity and self.collides(entity, x, y):
            return entity
        return None

    def collides_point(self, point, x=None, y=None):
        """ Check if 'self' is colliding with a specific point """
        if x is None or y is None:
            x = self.x
            y = self.y

        px, py = point
        if x <= px <= x + self.width and y <= py <= y + self.height:
            return True
        else:
            return False

    def collides_circle(self, circle, x=None, y=None):
        """
        Check if 'self' is colliding with a circle
        circle = tuple (x, y, radius)

        Can provide custom x/y or leave blank for self.x/self.y.
        """
        if x is None or y is None:
            x = self.x
            y = self.y

        circle_x, circle_y, radius = circle
        circle_x += radius
        circle_y += radius

        rx = self.x + self.width / 2
        ry = self.y + self.height / 2

        dist_x = abs(circle_x - rx)
        dist_y = abs(circle_y - ry)
        half_width = self.width / 2
        half_height = self.height / 2

        if dist_x > (half_width + radius):
            return False
        if dist_y > (half_height + radius):
            return False

        if dist_x <= half_width:
            return True
        if dist_y <= half_height:
            return True

        corner_distance = (dist_x - half_width)**2 + (dist_y - half_height)**2

        return corner_distance <= (radius**2)

    def collides_rect(self, rect, x=None, y=None):
        """
        Check if 'self' is colliding with a rectangle.
        rect = tuple (x, y, width, height)

        Can provide custom x/y or leave blank for self.x/self.y
        """
        if x is None or y is None:
            x = self.x
            y = self.y

        rx, ry, rwidth, rheight = rect

        left_a = x
        right_a = x + self.width
        top_a = y
        bottom_a = y + self.height

        left_b = rx
        right_b = rx + rwidth
        top_b = ry
        bottom_b = ry + rheight

        if (bottom_a <= top_b or top_a >= bottom_b or
                right_a <= left_b or left_a >= right_b):
            return False
        else:
            return True

    def collides_solid(self, x=None, y=None):
        """ Check if 'self' is colliding with any entity flagged as 'solid' """
        if x is None or y is None:
            x = self.x
            y = self.y

        collisions = []
        for entity in self.container:
            if entity == self or not entity.active:
                continue
            elif entity.solid and self.collides(entity, x, y):
                collisions.append(entity)
        return collisions

    def distance_from(self, entity):
        """ Get the abs distance between the center of two entities """
        sx, sy = self.center()
        ex, ey = entity.center()
        a = abs(sx - ex)
        b = abs(sy - ey)
        return math.sqrt(a**2 + b**2)

    def distance_from_point(self, px, py):
        """ Get the abs distance between the center of 'self' and any point """
        a = abs(self.x - px)
        b = abs(self.y - py)
        return math.sqrt(a**2 + b**2)

    def member_of(self, *groups):
        """ Check is this entity is a member of any of the groups specified """
        for group in self.group:
            if group in groups:
                return True
        return False

    def render(self):
        """ Perform render logic """
        return

    def update(self):
        """ Perform update logic """
        return


class State(object):
    """ Boilerplate state class for World """

    def __init__(self, name, world):
        self.name = name
        self.world = world

    def enter(self, previous_state, *args):
        return

    def exit(self, next_state, *args):
        return

    def render(self):
        return

    def update(self):
        return


class World(object):
    """
    Worlds contain logic for governing specific states within a game.
    Example:
        GameplayWorld
        MainMenuWorld
        etc.

    Worlds control Stages.

    Worlds can switch between each other by invoking Engine.change_world()

    Note: State's are not automatically updated or rendered and the logic for
    invoking these methods should be custom.
    """

    def __init__(self, name):
        self.name = name
        self.ui = None
        self.stage = stage.Stage(self)
        self.state = None
        self.states = {}

    def add_state(self, state):
        self.states[state.name] = state
        if self.state is None:
            self.state = state

    def change_stage(self, stage):
        """ Change the current stage and clear the previous stage """

        if self.stage:
            self.stage.clear()
            self.stage.exit()
        self.stage = stage
        self.stage.enter()

    def change_state(self, state_name, *args):
        """ Change the current state """

        if state_name in self.states and \
           state_name != self.state.name:

            previous_state = self.state
            incoming_state = self.states[state_name]

            previous_state.exit(incoming_state, *args)
            incoming_state.enter(previous_state, *args)

            self.state = incoming_state
        else:
            DEBUG('[ERROR] {0} state ({1}) not found', self.name, state_name)

    def enter(self):
        """ Called after entering this world """
        return

    def exit(self):
        """ Called before exiting this world """
        return

    def register_UI(self, ui):
        """ Attach a UI component to this world """
        self.ui = ui

    def shutdown(self):
        """ Shutdown procedure called during exit of Engine """
        try:
            self.stage.clear()
            self.stage = None
        except AttributeError:
            pass

        try:
            self.state.exit(None)
            self.state = None
            self.states = None
        except AttributeError:
            pass

    def update(self):
        try:
            self.ui.update()
        except AttributeError:
            if self.ui == None:
                pass
            else:
                raise

        self.stage.update()

    def render(self):
        try:
            self.ui.render()
        except AttributeError:
            if self.ui == None:
                pass
            else:
                raise

        self.stage.render()
