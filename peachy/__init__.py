import math 
import os
import platform
import sys

import pygame
from pygame.locals import *

import graphics
import assets
import utils

if __debug__:
    def debug_draw_grid(cell_width, cell_height, offset_x=0, offset_y=0):
        view_width, view_height = PC.view_size
        
        x = offset_x
        y = offset_y

        while x < view_width:
            graphics.draw_line(x, offset_y, x, view_height)
            x += cell_width

        while y < view_height:
            graphics.draw_line(offset_x, y, view_width, y)
            y += cell_height


class PC(object):
    """
    PC (Peachy Controller)

    This is the central controlling class for the Peachy framework. This class
    controls the window, world, and entity room.
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
    def scene(self):
        return PC.engine.world.scene

    @staticmethod
    def set_title(title):
        pygame.display.set_caption(title)

    @staticmethod
    def quit():
        pygame.event.post(pygame.event.Event(QUIT))


class Engine(object):

    def __init__(self, view_size, title='', fps=60, scale=1, debug=False):
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

        # initialize pygame
        os.environ['SDL_VIDEO_CENTERED'] = "1" 

        try:
            pygame.display.init()
            pygame.font.init()
            # pygame.joystick.init()
            if plat != 'Linux':
                pygame.mixer.init(44100, 16, 2, 512)
        except Exception:
            if pygame.display.get_init() is None or \
               pygame.font.get_init() is None:
                print "Could not initialize pygame core. Aborting."
                return -1
            else:
                print "Could not initialize pygame modules"

        # General initialization
        pygame.display.set_caption(title)
        utils.Input.init()

        # Init display (pygame)
        self.view_size = (PC.width, PC.height)
        self.window_size = (PC.width * scale, PC.height * scale)
        
        self._window_surface = pygame.display.set_mode(self.window_size)
        self._render_surface = pygame.Surface(self.view_size)

        graphics.DEFAULT_CONTEXT = self._render_surface
        graphics.set_context(self._render_surface)

        graphics.__font = graphics.Font('fonts/ProggyClean.ttf', 16)

    def add_world(self, world):
        self.worlds[world.name] = world
        if self.world is None:
            self.world = world
            PC.world = self.world
        return self.worlds[world.name]

    def change_world(self, world):
        if world in self.worlds:
            self.world.exit()
            self.world = self.worlds[world]
            self.world.enter()
            return self.world
        else:
            print '[WARN] World not found: {0}'.format(world)
            return None

    def fullscreen(self):
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
        return

    def run(self):
        game_timer = pygame.time.Clock()
        utils.Input.poll_keyboard()

        self.preload()

        running = True
        try:
            while running:
                if self.world is not PC.world:
                    PC.world = self.world

                # Parse events
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                        break

                utils.Input.poll_keyboard()

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

                # Maintain fps
                game_timer.tick(PC.fps)
                if PC.debug:
                    fps = round(game_timer.get_fps())
                    pygame.display.set_caption(PC.title + ' {' + str(fps) + '}')
            
            self.shutdown()
            pygame.event.get() # Throw away any pending events
            pygame.mixer.quit() 
            pygame.quit()
        
        except:
            import traceback
            print "[ERROR] Unexpected error. {0} shutting down.".format(PC.title)
            traceback.print_exc()
        sys.exit()

    def shutdown(self):
        for _, world in self.worlds.iteritems():
            world.close()
    

class Entity(object):
    """
    Interactable game object
    """

    def __init__(self, x=0, y=0):
        self.group = ''           # Every entity belongs to a group
        self.name = ''            # Unique entities have a name (1/room)

        self.event_handle = None  # Used by events to access this entity, set on map load

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

        self.container = None     # The owner of this entity. Must be set before performing any operations involving groups of entities

    @property
    def group(self):
        return self.__groups
    
    @group.setter
    def group(self, groups):
        self.__groups = groups.split()

    def center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)

    def destroy(self):
        self.container.remove(self)
        self.active = False
        self.world = None

    def collides(self, e, x, y):  
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
        if x is None or y is None:
            x = self.x
            y = self.y

        for entity in self.container:
            if entity.name == name and self.collides(entity, x, y):
                return entity
        return None

    def collides_point(self, point, x=None, y=None):
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
        circle is tuple (x, y, radius)
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
        a = abs(self.x - entity.x)
        b = abs(self.y - entity.y)
        return math.sqrt(a**2 + b**2)

    def distance_from_point(self, px, py):
        a = abs(self.x - px)
        b = abs(self.y - py)
        return math.sqrt(a**2 + b**2)
    
    def member_of(self, *groups):
        for group in self.group:
            if group in groups:
                return True
        return False

    def render(self):
        return
            
    def update(self):
        return


class EntityContainer(object):
    def __init__(self):
        self.entities = []

    def __contains__(self, item):
        return item in self.entities

    def __iter__(self):
        return self.entities.__iter__()

    def add(self, entity):
        entity.container = self
        self.entities.append(entity)
        return entity

    def clear(self):
        del self.entities[:]

    def get_group(self, *groups):
        ents = []
        for e in self.entities:
            if e.member_of(*groups):
                ents.append(e)
        return ents

    def get_name(self, name):
        for e in self.entities:
            if e.name == name:
                return e
        return None

    def remove(self, entity):
        try:
            self.entities.remove(entity)
        except ValueError:
            pass  # Do nothing

    def remove_group(self, group):
        for entity in self.entities:
            if entity.member_of(group):
                self.entities.remove(entity)

    def remove_name(self, entity_name):
        for entity in self.entities:
            if entity.name == entity_name:
                self.entities.remove(entity)
                break

    def render(self):
        for entity in self.entities:
            if entity.visible:
                entity.render()

    def update(self):
        for entity in self.entities:
            if entity.active:
                entity.update()


class State(object):

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


class Scene(object):

    def __init__(self, world):
        self.world = world
        self.entities = EntityContainer()
    
    def load(self):
        return

    def exit(self):
        self.entities.clear()

    def update(self):
        self.entities.update()

    def render(self):
        self.entities.render()

class World(object):
    """
    State machine
    """

    def __init__(self, name):
        self.name = name
        self.scene = Scene(self)
        self.state = None
        self.states = {}

    def add_state(self, state):
        self.states[state.name] = state
        if self.state is None:
            self.state = state

    def change_state(self, state_name, *args):
        if state_name in self.states and \
           state_name != self.state.name:

            previous_state = self.state
            incoming_state = self.states[state_name]

            previous_state.exit(incoming_state, *args)
            incoming_state.enter(previous_state, *args)
            
            self.state = incoming_state
        else:
            print state_name in self.states
            print '[ERROR] change_state request invalid'

    def enter(self):
        return

    def exit(self):
        return

    def close(self):
        if self.scene is not None:
            self.scene.exit()
            self.scene = None
        if self.state is not None:
            self.state.exit(None)
            self.state = None

    def update(self):
        self.scene.update()

    def render(self):
        self.scene.render()

