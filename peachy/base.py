"""Base Peachy module

This is the base module for Peachy. It contains the Engine, World, WorldState,
Room, and Entity classes; the building blocks of any Peachy project.

Note:
    Import using `peachy` not `peachy.base`. All base classes are loaded into
    imported into peachy already. Use:
        >>> import peachy  # RIGHT!
        >>> import peachy.base  # wrong
"""

import logging
import os
import sys

import peachy
import peachy.fs
import peachy.graphics
import peachy.utils

import pygame
import pygame.locals

from peachy.utils import list_wrap


# A global reference to the current peachy.Engine is None until a peachy.Engine
# has been initialized
_PC = None


def PC():
    """Global reference to current peachy.Engine."""
    return _PC


def _set_PC(PC):
    global _PC
    _PC = PC


class Engine(object):
    """The central controlling class for Peachy.

    Controls priority aspects of the application such as: initialization,
    loading config, running game loop, controlling World objects, etc.

    Attributes:
        worlds (list[peachy.World]): References to all World objects bound to
            this engine.
        world (peachy.World): Reference to the currently active World.
        canvas_size (tuple[int, int]): Contains width and height, respectively.
    """

    def __init__(self, canvas_size=(640, 480), title='', fps=60, scale=1,
                 debug=False):
        """Initialize Engine

        Initializes peachy configuration and initializes pygame.

        Args:
            canvas_size (tuple, optional): A tuple containing width and height,
                respectively. Is (640, 480) by default. Can also be
                specified via PeachyConfiguration.
            title (str, optional): The caption for the window. Is blank by
                default. Can also be specified via PeachyConfiguration.
            fps (int, optional): Frames per second. Can also be specified via
                PeachyConfiguration.
            scale (int, optional): Amount to scale the screen by. Set to 1 by
                default. Default can be specified via PeachyConfiguration.
            debug (bool, optional): Enable debug mode (cannot change once game
                run() is called). Disabled by default. Can also be set via
                PeachyConfiguration.
        """
        # Set global PC reference
        _set_PC(self)

        self.worlds = {}
        self.world = None

        # TODO config
        self.background_color = (0, 0, 0)
        self.debug_enabled = debug
        self.fps = fps if fps > 0 else 60
        self.__title = title
        self.__scale = scale
        # End config

        # Canvas
        self.canvas_size = canvas_size
        canvas_width = canvas_size[0]
        canvas_height = canvas_size[1]
        self._canvas_surface = None

        # Window
        self.window_size = (canvas_width * scale, canvas_height * scale)
        self._window_surface = None

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
                logging.error("Could not initialize pygame display. Abort!")
            elif pygame.font.get_init() is None:
                logging.error("Could not initialize pygame font. Abort!")
            elif pygame.freetype.get_init() is None:
                logging.error("Could not initialize pygame freetype. Abort!")
            elif pygame.mixer.get_init() is None:
                logging.error("Could not initialize pygame mixer. Abort!")
            raise

        # General initialization
        pygame.event.set_allowed([pygame.locals.QUIT,
                                  pygame.locals.VIDEORESIZE])
        pygame.display.set_caption(title)
        peachy.utils.Input.init()

        # Initialize pygame display
        flags = pygame.locals.DOUBLEBUF

        self._window_surface = pygame.display.set_mode(self.window_size, flags)
        self._canvas_surface = pygame.Surface(self.canvas_size)

        peachy.graphics.set_default_context(self._canvas_surface)
        peachy.graphics.set_context(self._canvas_surface)

        try:
            peachy.graphics.__font = peachy.graphics.Font(
                'peachy/fonts/ProggyClean.ttf', 16)
        except IOError:
            logging.warning("Font not found")
            # TODO get default monospace font for system.

    @property
    def canvas_width(self):
        """int: The width of the render surface in pixels. Refers to
        canvas_size[0].
        """
        return self.canvas_size[0]

    @canvas_width.setter
    def canvas_width(self, width):
        self.resize(width, self.canvas_height)

    @property
    def canvas_height(self):
        """int: The height of the render surface in pixels. Refers to
        canvas_size[1].
        """
        return self.canvas_size[1]

    @canvas_height.setter
    def canvas_height(self, height):
        self.resize(self.canvas_width, height)

    @property
    def title(self):
        """str: The title of the window.
        If this property is altered the window caption will change. However,
        this will overwrite FPS display in DEBUG mode.
        """
        return self.__title

    @title.setter
    def title(self, t):
        self.__title = t
        pygame.display.set_caption(t)

    @property
    def scale(self):
        """int: The scale of the base rendering surface
        Everything rendered to the screen is affected by scale. Changing scale
        re-initializes the window.
        """
        return self.__scale

    @scale.setter
    def scale(self, s):
        self.__scale = s
        self.window_size = (self.canvas_width * s, self.canvas_height * s)
        self._window_surface = pygame.display.set_mode(self.window_size)

    def add_world(self, world, name=''):
        """Add world to the Engine

        Adds world to self.worlds. If self.worlds is empty then this world is
        set as the active world (self.world). Key for this world is name or
        world.name if name is left unspecified

        Args:
            world (peachy.World): The World object to add to the engine
            name (str. optional): The name to register the World under. Used
                when accessing worlds. If left blank, the Engine uses
                World.name

        Return:
            peachy.World: A reference to the newly added World
        """

        if not name:
            name = world.name

        self.worlds[name] = world
        if self.world is None:
            self.world = world

        return self.worlds[name]

    def change_world(self, world_name):
        """Change current active world

        Change current active world to world specified by world_name. Calls
        exit() and enter() on previous world and upcoming world, respectively.
        Requested world must already be added through add_world().

        Args:
            world_name (str): the name that the requested World was registered
                under.

        Return:
            peachy.World: A reference to the World inside self.worlds or None if
                there is no World associated to world_name.

        Todo:
            Raise an error instead of returning None on invalid world_name.
        """

        if world_name in self.worlds:
            self.world.exit()
            self.world = self.worlds[world_name]
            self.world.enter()
            return self.world
        else:
            logging.warning('World not found: {0}'.format(world_name))
            return None

    def force_shutdown(self):
        """Immediatly shutdown engine"""
        self.__shutdown()  # Shutdown all peachy modules
        pygame.event.get()  # Throw away any pending events
        pygame.quit()  # Shutdown pygame modules
        sys.exit()

    def get_world(self, world_name):
        """Get a :class:`World` by it name."""
        return self.worlds.get(world_name)

    def quit(self):
        """Send shutdown signal. Peachy will exit after completing the current
        cycle.
        """
        pygame.event.post(pygame.event.Event(pygame.locals.QUIT))

    def preload(self):
        """Abstract method for preloading.

        Called at the beginning of run() before entering the main game loop.
        Use to perform startup operations.
        """
        return

    def resize(self, width, height):
        """Resize window

        Changes window and render surface size to width*height.

        Args:
            width (int): width of the new window.
            height (int): height of the new window.
        """
        screen = pygame.display.get_surface()
        flags = screen.get_flags()
        bits = screen.get_bitsize()

        self.window_size = (width, height)
        self._window_surface = \
            pygame.display.set_mode(self.window_size, flags, bits)

        self.canvas_size = (width, height)
        self._canvas_surface = pygame.Surface(self.canvas_size)
        peachy.graphics.set_default_context(self._canvas_surface)
        peachy.graphics.set_context(self._canvas_surface)

    def run(self):
        """Start game.

        This function runs the game loop and is the root from which operations
        are invoked. Exits only once game is done running.

        Calls preload() before entering game loop.
        """

        game_timer = pygame.time.Clock()
        peachy.utils.Input.poll()

        self.preload()
        self.world.enter()

        running = True
        while running:
            if self.world is not self.world:
                self.world = self.world

            # Parse events
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    running = False
                    break
                elif event.type == pygame.locals.VIDEORESIZE:
                    self.resize(event.w, event.h)

            peachy.utils.Input.poll()

            # Update
            self.__update()

            # Render - Draw World
            self.__render()

            # Render - Transformations
            # TODO speed up scaling somehow
            pygame.transform.scale(self._canvas_surface, self.window_size,
                                   self._window_surface)

            # Render - Finalize
            pygame.display.flip()

            # Maintain fps (display if DEBUG is active)
            game_timer.tick(self.fps)
            if self.debug_enabled:
                fps = round(game_timer.get_fps())
                pygame.display.set_caption(self.__title +
                                           ' {' + str(fps) + '}')

        self.__shutdown()  # Shutdown all peachy modules
        pygame.event.get()  # Throw away any pending events
        pygame.mixer.quit()
        pygame.quit()  # Shutdown all pygame modules

    def toggle_fullscreen(self):
        """Toggle fullscreen

        Todo:
            * Maintain aspect ratio
        """

        screen = pygame.display.get_surface()
        caption = pygame.display.get_caption()

        flags = screen.get_flags()
        bits = screen.get_bitsize()

        pygame.display.quit()
        pygame.display.init()

        if flags ^ pygame.locals.FULLSCREEN:
            monitor_info = pygame.display.Info()

            ratio = min(
                float(monitor_info.current_w) / float(self.canvas_width),
                float(monitor_info.current_h) / float(self.canvas_height))

            window_width = int(self.canvas_width * ratio)
            window_height = int(self.canvas_height * ratio)
            self.window_size = (window_width, window_height)
        else:
            self.window_size = (self.canvas_width * self.scale,
                                self.canvas_height * self.scale)

        pygame.display.set_caption(*caption)

        self._window_surface = pygame.display.set_mode(
            self.window_size, flags ^ pygame.locals.FULLSCREEN, bits)
        self._canvas_surface = pygame.Surface(self.canvas_size)

        peachy.graphics.set_default_context(self._canvas_surface)
        peachy.graphics.set_context(self._canvas_surface)

    def __render(self):
        self._canvas_surface.fill(self.background_color)
        self.world.render()

    def __shutdown(self):
        """Execute shutdown procedure

        Called right before exiting run() and shutting down pygame modules.
        """

        for _, world in self.worlds.items():
            world.shutdown()

    def __update(self):
        self.world.update()


class Entity(object):
    """Interactive game object

    Entity is the main actor in the Peachy framework. Entity's are held within
    World.Room and are updated and rendered every cycle. Entity's contain &
    interact with multiple utility functions for collision detection,
    organization, and rendering. Entity inherits from Rect which handles basic
    collision detection.

    Attributes:
        name (str): A unique string used to identify this Entity. 1 per Room.
        group (str): A string used to organize this entity into categories, an
            Entity can be a part of multiple groups. Groups are separated with
            a space.
            Ex: "group_a group_b group_c"
        active (bool): Is this entity being updated? If this is set to False
            then self.update() will not be called each cycle.
        visible (bool): Is this entity being rendered? If this is set to False
            then self.render() will not be called each frame.
        solid (bool): Is this entity collidable? If this is set to False
            then this entity is ignored during collision detection checks.
        order (int): Order of entity in Room.entities. Lower order is rendered
            and updated first.
        container (peachy.Room): A reference to the owner of this entity.
            Must be set before performing any operations involving groups
            (Entity.group).
    """

    def __init__(self):
        """Initialize Entity"""
        self.group = ''
        self.__groups = []
        self.name = ''

        self.active = True
        self.visible = True
        self.solid = False

        self.order = 0

        self.container = None

    @property
    def group(self):
        return self.__groups

    @group.setter
    def group(self, groups):
        self.__groups = groups.split()

    def destroy(self):
        """Destroy this entity.

        Remove entity from self.container and set as inactive.

        Note:
            Resources will not be released until all references to this entity
            have been removed.
        """
        self.container.remove(self)
        self.active = False

    def member_of(self, *groups):
        """Check if this entity is a member of a group.

        Args:
            *groups (str): Argument list of groups to check membership.

        Returns:
            bool: True if entity is a member of any of the groups specified.
        """
        for group in self.group:
            if group in groups:
                return True
        return False

    def render(self):
        """Perform render logic."""
        return

    def update(self):
        """Perform update logic."""
        return


class Room(list):
    """Entity container.

    Attributes:
        world (peachy.World): Containing World.
        sort_required (bool): Does entities list need to be sorted? If True,
            entities list will be sorted at the end of this cycle.
    """

    def __init__(self, world):
        """Initialize Room.

        Args:
            world (peachy.World): The world to register this Room to.
        """
        super().__init__()
        self.world = world
        self.sort_required = False

        self.append = self.add

    def enter(self):
        """Called after entering this room."""
        return

    def exit(self):
        """Called before exiting this room."""
        return

    def add(self, entity):
        """Add an entity to this Stage.

        Adds an entity to self.entities and sets entity.container to self.
        self.sort() will be queued.

        Args:
            entity (peachy.Entity): Entity to add to this Room.

        Returns:
            peachy.Entity: a reference to the entity added to self.entities.
        """
        entity.container = self
        super().append(entity)
        self.sort_required = True
        return entity

    def get_group(self, *groups):
        """Get every entity that is a member of a group.

        Iterate through all entities that are members of any of the specified
        groups.

        Args:
            *groups(str): The groups to check for membership

        Returns:
            list[peachy.Entity]: A generator that yields members of
                the specified groups.
        """
        for e in self:
            if e.member_of(*groups):
                yield e

    def get_name(self, name):
        """Get entity by name

        Finds the first entity under name in self.entities.

        Args:
            name (str): The Entity.name to find

        Returns:
            peachy.Entity: An entity that has the unique name
        """
        for e in self:
            if e.name == name:
                return e
        return None

    def remove(self, entity):
        """Remove entity from this Room.

        Removes entity from self.entities. Queues sort.

        Args:
            entity (peachy.Entity): The entity to remove.
        """

        try:
            super().remove(entity)
            self.sort_required = True
        except ValueError:
            logging.warning('Attempted to remove Entity \{{0}\} \
                   that is not in Room \{{1}\}'.format(entity, self))
            pass  # Do nothing

    def remove_group(self, group):
        """Remove group of entities.

        Remove every entity that is a member of the specified group from
        self.entities. Queues sort.

        Args:
            group (str): The group to remove
        """

        for entity in list_wrap(self):
            if entity.member_of(group):
                self.remove(entity)

    def remove_name(self, entity_name):
        """ Remove an entity from this Room by name.

        Find entity by name and removes from self.entities. Queues sort.

        Args:
            entity_name (str): The unique name of an entity to remove.
        """

        for entity in self:
            if entity.name == entity_name:
                self.remove(entity)
                break

    def render(self):
        """Render all visible entities.

        Call Entity.render() on all entities inside self.entities that have
        Entity.visible set to True.
        """
        for entity in list_wrap(self):
            if entity.visible:
                entity.render()

    def update(self):
        """Update all active entities.

        Call Entity.update() on all entities inside self.entities that have
        Entity.active set to True.

        Sorts all entities after updating if sort has been queued.
        """
        for entity in list_wrap(self):
            if entity.active:
                entity.update()

        if self.sort_required:
            self.sort()
            self.sort_required = False

    def sort(self):
        """Sort entities.

        Sort all entities in self.entities based on entity.order. Called
        automatically inside self.update() if sort_required is True.
        """
        super().sort(key=lambda entity: entity.order)


class World(object):
    """Contains Room and state-management. Invoked by Engine.

    Worlds contain logic for governing specific states within a game.
    Example:
        GameplayWorld
        MainMenuWorld
        etc.

    Worlds control Rooms.

    Worlds can also have states via peachy.WorldState
    Note: State's are not automatically updated or rendered and the logic for
            invoking these methods should be custom.
            >>> self.state.update()

    Attributes:
        name (str): The name of the World, used by peachy.Engine for accessing
            this world inside peachy.Engine.worlds.
        room (peachy.Room): The current collection of Entities active in this
            World.
        state (peachy.WorldState): The current state of this World. Set to None
            by default.
        states (list[peachy.WorldState]): The different states bound to this
            World.
        ui (peachy.ui.UI): a handle to a custom UserInterface. Set to None by
            default.
    """

    def __init__(self, name):
        """Initialize World

        Args:
            name (str): The name of this World
        """
        self.name = name
        self.ui = None
        self.room = peachy.Room(self)
        self.state = None
        self.states = {}

    def add_state(self, state):
        """Add state to World

        Adds state to self.states. If self.states is empty then this state is
        set as the active state (self.state).

        Args:
            state (peachy.WorldState): The state to add to self.states.
        """
        self.states[state.name] = state
        if self.state is None:
            self.state = state

    def change_room(self, room):
        """Change the current room

        Changes the current room to room argument. Clears previous room and
        calls  exit() and enter() on previous room and upcoming room,
        respectively.

        Args:
            room (peachy.Room): the room to set as active room.
        """
        if self.room:
            self.room.clear()
            self.room.exit()
        self.room = room
        self.room.enter()

    def change_state(self, state_name, *args):
        """Change the current state

        Changes the current active state to state specified by state_name. Calls
        exit() and enter() on previous state and upcoming state, respectively.
        State must already be added through add_state() for this function to
        work correctly.

        Args:
            state_name (str): the name that the requested WorldState was
                registered under.
            *args: Arguments to pass to the upcoming state on state.enter().

        Todo:
            * Raise an error if state_name is invalid.
        """

        if state_name in self.states and \
           state_name != self.state.name:

            previous_state = self.state
            incoming_state = self.states[state_name]

            previous_state.exit(incoming_state, *args)
            incoming_state.enter(previous_state, *args)

            self.state = incoming_state
        else:
            logging.warning('{0} state ({1}) not found', self.name, state_name)

    def enter(self):
        """Called after entering this world."""
        return

    def exit(self):
        """Called before exiting this world."""
        return

    def register_UI(self, ui):
        """Attach a UI component to this world."""
        self.ui = ui

    def shutdown(self):
        """Shutdown procedure. Called during peachy shutdown procedure."""
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
        """Update ui and state/room."""
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
        """Render ui and state/room."""
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
