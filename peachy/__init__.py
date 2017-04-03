""" Peachy gamedev """

import os
import sys

import pygame
import pygame.locals

# Import all submodules
import peachy.audio
import peachy.fs
import peachy.geo
import peachy.graphics
import peachy.stage
import peachy.utils
from peachy.PC import PC


def DEBUG(*objs):
    """ Print debug information to outstream (Only if DEBUG is active) """
    if PC.debug:
        print("[DEBUG]", *objs, file=sys.stderr)


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
        self.__title = title
        self.__scale = scale

        PC.engine = self
        PC.width = view_size[0]
        PC.height = view_size[1]
        PC.fps = fps
        PC.debug = debug

        self._render_surface = None
        self._window_surface = None

        self.resizable = resizable

        if fps <= 0:
            PC.fps = 60

        # Initialize pygame
        try:
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            pygame.mixer.pre_init(44100, -16, 8, 512)
            pygame.display.init()
            pygame.freetype.init()
            pygame.mixer.init()
            # TODO Joystick module prints obstructing dialog, must build from
            # source.
            # pygame.joystick.init()
        except Exception:
            if pygame.display.get_init() is None:
                print("[ERROR] Could not initialize pygame display. Abort!")
            elif pygame.font.get_init() is None:
                print("[ERROR] Could not initialize pygame font. Abort!")
            elif pygame.freetype.get_init() is None:
                print("[ERROR] Could not initialize pygame freetype. Abort!")
            elif pygame.mixer.get_init() is None:
                print("[ERROR] Could not initialize pygame mixer. Abort!")
            return -1

        # General initialization
        pygame.display.set_caption(title)
        peachy.utils.Key.init()
        peachy.utils.Mouse.init()
        pygame.event.set_allowed([pygame.locals.QUIT,
                                  pygame.locals.VIDEORESIZE])

        # Initialize display (pygame)
        self.view_size = (PC.width, PC.height)
        self.window_size = (PC.width * scale, PC.height * scale)

        flags = pygame.locals.DOUBLEBUF
        if resizable:
            flags += pygame.locals.RESIZABLE

        self._window_surface = pygame.display.set_mode(self.window_size, flags)
        self._render_surface = pygame.Surface(self.view_size)

        peachy.graphics.set_default_context(self._render_surface)
        peachy.graphics.set_context(self._render_surface)

        try:
            peachy.graphics.__font = peachy.graphics.Font(
                'peachy/fonts/ProggyClean.ttf', 16)
        except IOError:
            DEBUG("Default font not found")
            # TODO exit

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, t):
        self.__title = t
        pygame.display.set_caption(t)

    @property
    def scale(self):
        return self.__scale

    @scale.setter
    def scale(self, s):
        self.__scale = s
        self.window_size = (PC.width * s, PC.height * s)
        self._window_surface = pygame.display.set_mode(self.window_size)

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
            PC.world = self.world
            return self.world
        else:
            DEBUG('World not found: {0}'.format(world_name))
            return None

    def get_world(self, world_name):
        return self.worlds.get(world_name)

    def toggle_fullscreen(self):
        """ Toggles fullscreen """
        # TODO maintain aspect ratio

        screen = pygame.display.get_surface()
        caption = pygame.display.get_caption()

        flags = screen.get_flags()
        bits = screen.get_bitsize()

        pygame.display.quit()
        pygame.display.init()

        if flags ^ pygame.locals.FULLSCREEN:
            monitor_info = pygame.display.Info()

            ratio = min(float(monitor_info.current_w) / float(PC.width),
                        float(monitor_info.current_h) / float(PC.height))

            window_width = int(PC.width * ratio)
            window_height = int(PC.height * ratio)
            self.window_size = (window_width, window_height)
        else:
            self.window_size = (PC.width * PC.scale, PC.height * PC.scale)

        pygame.display.set_caption(*caption)

        self._window_surface = pygame.display.set_mode(
            self.window_size, flags ^ pygame.locals.FULLSCREEN, bits)
        self._render_surface = pygame.Surface(self.view_size)

        peachy.graphics.set_default_context(self._render_surface)
        peachy.graphics.set_context(self._render_surface)

    def preload(self):
        """
        Called at the beginning of run() before entering the main game loop.
        Use to perform startup operations.
        """
        return

    def resize(self, width, height):
        screen = pygame.display.get_surface()
        flags = screen.get_flags()
        bits = screen.get_bitsize()

        self.window_size = (width, height)
        self._window_surface = \
            pygame.display.set_mode(self.window_size, flags, bits)

        if self.resizable:
            self.view_size = (width, height)
            self._render_surface = pygame.Surface(self.view_size)
            peachy.graphics.set_default_context(self._render_surface)
            peachy.graphics.set_context(self._render_surface)
            PC.width = width
            PC.height = height

    def run(self):
        """ Start game loop (calls preload before running game loop) """

        game_timer = pygame.time.Clock()
        peachy.utils.Mouse._poll()
        peachy.utils.Key._poll()

        self.preload()
        self.world.enter()

        running = True
        try:  # a try to catch any missed exceptions
            while running:
                if self.world is not PC.world:
                    PC.world = self.world

                # Parse events
                for event in pygame.event.get():
                    if event.type == pygame.locals.QUIT:
                        running = False
                        break
                    elif event.type == pygame.locals.VIDEORESIZE:
                        self.resize(event.w, event.h)

                peachy.utils.Mouse._poll()
                peachy.utils.Key._poll()

                # Update
                self.__update()

                # Render - Draw World
                self.__render()

                # Render - Transformations
                # TODO speed up scaling somehow
                pygame.transform.scale(self._render_surface, self.window_size,
                                       self._window_surface)

                # Render - Finalize
                pygame.display.flip()

                # Maintain fps (display if DEBUG is active)
                game_timer.tick(PC.fps)
                if PC.debug:
                    fps = round(game_timer.get_fps())
                    pygame.display.set_caption(self.__title +
                                               ' {' + str(fps) + '}')

            self.shutdown()  # Shutdown all peachy modules
            pygame.event.get()  # Throw away any pending events
            pygame.mixer.quit()
            pygame.quit()  # Shutdown all pygame modules

        except:
            import traceback
            print("[ERROR] Unexpected error. {0} shutting down."
                  .format(self.__title))
            traceback.print_exc()
        sys.exit()

    def __render(self):
        self._render_surface.fill(PC.background_color)
        self.world.render()

    def shutdown(self):
        """ Shutdown procedure called right before exiting Peachy """

        for _, world in self.worlds.items():
            world.shutdown()

    def __update(self):
        self.world.update()


class Entity(peachy.geo.Rect):
    """
    Interactive game object.

    Inherits from Rect which handles basic collision detection
    """

    def __init__(self, x=0, y=0):
        super().__init__(x, y, 0, 0)  # Initializes x, y, width, height

        self.group = ''           # Every entity belongs to a group
        self.name = ''            # Unique entities have a name (1/room)

        self.velocity_x = 0       # x-axis velocity
        self.velocity_y = 0       # y-axis velocity

        self.active = True        # If the entity is being updated
        self.visible = True       # If the entity is being rendered
        self.solid = False        # If the entity is used for collides_solid()

        self.sprite = None        # sprite used for rendering
        self.order = 0            # Used for sorting entity render order

        # MUST be set before perfoming any operations involving groups of ents
        self.container = None  # The owner of this entity, usually a Room

    @property
    def group(self):
        return self.__groups

    @group.setter
    def group(self, groups):
        self.__groups = groups.split()

    def destroy(self):
        """
        Remove entity from parent container and set as inactive. Note that
        resources will not be released until all references to this entity
        have been removed.
        """
        self.container.remove(self)
        self.active = False
        self.world = None

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
        for entity in self.container.get_group(group):
            if entity is not self and entity.active and \
               self.collides(entity, x, y):
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

        collisions = []
        for entity in self.container.get_group(*groups):
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

    def collides_solid(self, x=None, y=None):
        """ Check if 'self' is colliding with any entity flagged as 'solid' """
        if x is None or y is None:
            x = self.x
            y = self.y

        collisions = []
        for entity in self.container:
            if entity is not self and entity.active and entity.solid and \
               self.collides(entity, x, y):
                collisions.append(entity)
        return collisions

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


class Room(object):
    """ Controller for the current room and its containing entities """

    def __init__(self, world):
        self.entities = []
        self.world = world
        self.sort_required = False

    def __contains__(self, item):
        return item in self.entities

    def __iter__(self):
        return self.entities.__iter__()

    def enter(self):
        """ Called after entering this room """
        return

    def exit(self):
        """ Called before exiting this room """
        return

    def add(self, entity):
        """ Add an entity to this Stage """
        entity.container = self
        self.entities.append(entity)
        self.sort_required = True

        return entity

    def clear(self):
        """ Remove all entities from this Stage """
        del self.entities[:]

    def get_group(self, *groups):
        """
        Iterate through all entities that are members of any of the specified
        groups
        """
        for e in self.entities:
            if e.member_of(*groups):
                yield e

    def get_name(self, name):
        """ Get the first entity of a specific name """
        for e in self.entities:
            if e.name == name:
                return e
        return None

    def remove(self, entity):
        """ Remove this entity from the Stage """
        try:
            self.entities.remove(entity)
            self.sort_required = True
        except ValueError:
            pass  # Do nothing

    def remove_group(self, group):
        """ Remove every entity that is a member of the specified group """
        # Create reference list to iterate over. This prevents errors from
        # occuring when operations are performed on the list during iteration.
        entities = list(self.entities)

        for entity in entities:
            if entity.member_of(group):
                self.remove(entity)

    def remove_name(self, entity_name):
        """ Remove the first entity with this name """
        for entity in self.entities:
            if entity.name == entity_name:
                self.remove(entity)
                break

    def render(self):
        """ Render all visible entities """
        # Create reference list to iterate over. This prevents errors from
        # occuring when operations are performed on the list during iteration.
        entities = list(self.entities)

        for entity in entities:
            if entity.visible:
                entity.render()

    def update(self):
        """ Update all active entities """
        # Create reference list to iterate over. This prevents errors from
        # occuring when operations are performed on the list during iteration.
        entities = list(self.entities)

        for entity in entities:
            if entity.active:
                entity.update()

        if self.sort_required:
            self.sort()
            self.sort_required = False

    def sort(self):
        """ Sort entities based on entity.order """
        self.entities.sort(key=lambda entity: entity.order)


class World(object):
    """
    Worlds contain logic for governing specific states within a game.
    Example:
        GameplayWorld
        MainMenuWorld
        etc.

    Worlds control Rooms.

    Worlds can switch between each other by invoking Engine.change_world()

    Note: State's are not automatically updated or rendered and the logic for
    invoking these methods should be custom.
    """

    def __init__(self, name):
        self.name = name
        self.ui = None
        self.room = peachy.Room(self)
        self.state = None
        self.states = {}

    def add_state(self, state):
        self.states[state.name] = state
        if self.state is None:
            self.state = state

    def change_room(self, room):
        """ Change the current room and clear the previous room """

        if self.room:
            self.room.clear()
            self.room.exit()
        self.room = room
        self.room.enter()

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
            self.room.clear()
            self.room = None
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
            if self.ui is None:
                pass
            else:
                raise

        try:
            self.state.update()
        except AttributeError:
            if self.state is None:
                self.room.update()
            else:
                raise

    def render(self):
        try:
            self.ui.render()
        except AttributeError:
            if self.ui is None:
                pass
            else:
                raise

        try:
            self.state.render()
        except AttributeError:
            if self.state is None:
                self.room.render()
            else:
                raise


class WorldState(object):
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
