import os
import platform
import pygame
import sys
from pygame.locals import *

import graphics
from utils import Input

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

"""
PC (Peachy Controller)

This is the central controlling class for the Peachy framework. This class
controls the window, world, and entity room.

"""
class PC(object):
    
    _window_surface = None
    _render_surface = None

    _frames_per_second = 30
    _scale = -1
    _title = ''

    background_color = (0, 0, 0)

    view_size = (0, 0)
    window_size = (0, 0)

    room = None
    world = None

    DEBUG = False

    @staticmethod
    def init(view_size, fps=0, scale=1, title='Game', debug=False):

        os.environ['SDL_VIDEO_CENTERED'] = "1"

        try:
            pygame.display.init()
            pygame.font.init()
            # pygame.joystick.init()
            pygame.mixer.init(44100, 16, 2, 512)
        except Exception:
            if pygame.display.get_init() is None or \
               pygame.font.get_init() is None:
                print "Could not initialize pygame core. Aborting."
                return -1
            else:
                print "Could not initialize pygame modules"

        '''
        pygame.mixer.pre_init(44100, 16, 2, 512)
        if platform.system() == 'Linux':
            pygame.display.init()
            pygame.font.init()
            # TODO fix Linux mixer (very low priority)
        else:
            pygame.init()
        '''

        # General initialization
        PC._title = title
        PC._scale = scale

        # Init joysticks
        # TODO Fix joystick functionality
        # joystick_count = pygame.joystick.get_count()
        # for i in range(joystick_count):
        #     Input.joystick_raw.append(pygame.joystick.Joystick(i))
        #     Input.joystick_raw[i].init()
        #     Input.joystick.append({
        #         'AXIS': [], 
        #         'BUTTON': [] 
        #     })

        # Init pygame display
        pygame.display.set_caption(title)

        PC.view_size = view_size
        PC.window_size = (view_size[0] * scale, view_size[1] * scale)
        
        PC._window_surface = pygame.display.set_mode(PC.window_size)
        PC._render_surface = pygame.Surface(PC.view_size)

        graphics._MAIN_CONTEXT = PC._render_surface
        graphics.set_context(PC._render_surface)
        
        # Init peachy
        Input.init()
        PC.room = EntityRoom()
        PC.world = World()

        if fps > 0:
            PC._frames_per_second = fps

        # Init debug
        if debug:
            PC.DEBUG = debug
            print platform.system()

    @staticmethod
    def run():
        game_timer = pygame.time.Clock()
        Input.poll_keyboard()

        running = True

        try:
            while running:

                # Parse events
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                        break
                    #elif event.type == MOUSEMOTION or \
                    #     event.type == MOUSEBUTTONUP or \
                    #     event.type == MOUSEBUTTONDOWN:
                    #    Input.poll_mouse()
                utils.Input.poll_keyboard()


                # Update
                PC.world.update()

                # Render - Draw World
                PC._render_surface.fill(PC.background_color)
                PC.world.render()

                # Render - Transformations
                # TODO speed up scaling somehow
                render_size = PC.window_size
                pygame.transform.scale(PC._render_surface, render_size, PC._window_surface)

                # Render - Finalize
                pygame.display.flip()

                # Maintain fps
                game_timer.tick(PC._frames_per_second)
                if PC.DEBUG:
                    fps = round(game_timer.get_fps())
                    pygame.display.set_caption(PC._title + ' {' + str(fps) + '}')
            
            PC.world.exit()
            pygame.quit()

        except:
            import traceback
            print "[ERROR] Unexpected error. {0} shutting down.".format(PC._title)
            traceback.print_exc()
            sys.exit()

    @staticmethod
    def toggle_fullscreen():
        screen = pygame.display.get_surface()
        caption = pygame.display.get_caption()
        
        flags = screen.get_flags()
        bits = screen.get_bitsize()

        pygame.display.quit()
        pygame.display.init()

        if flags^FULLSCREEN:
            monitor_info = pygame.display.Info()

            ratio = min(float(monitor_info.current_w) / float(PC.view_size[0]),
                        float(monitor_info.current_h) / float(PC.view_size[1]))

            window_width = int(PC.view_size[0] * ratio)
            window_height = int(pls.view_size[1] * ratio)
            
            PC.window_size = (window_width, window_height)
        else:
            PC.window_size = (PC.view_size[0] * PC._scale, PC.view_size[1] * PC._scale)
        pygame.display.set_caption(*caption)

        PC._window_surface = pygame.display.set_mode(PC.window_size, flags^FULLSCREEN, bits)
        PC._render_surface = pygame.Surface(PC.view_size)

        graphics._MAIN_CONTEXT = PC._render_surface
        graphics.set_context(PC._render_surface)

    @staticmethod
    def quit():
        pygame.event.post(pygame.event.Event(QUIT))


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

    @property
    def group(self):
        return self.__groups
    
    @group.setter
    def group(self, groups):
        self.__groups = groups.split()

    def destroy(self):
        self.active = False
        PC.room.remove(self)

    # TODO change to validate_coordinates(self, x, y)
    def _check_bounds(self, x, y):
        if x is None or y is None:
            return (self.x, self.y)
        else:
            return (x, y)

    def collides(self, e, x=None, y=None):  
        x, y = self._check_bounds(x, y)

        if e is None or e == self:
            return False

        left_a = x
        right_a = x + self.width
        top_a = y
        bottom_a = y + self.height

        left_b = e.x
        right_b = e.x + e.width
        top_b = e.y
        bottom_b = e.y + e.height
        
        if left_a < right_b and \
           right_a > left_b and \
           top_a < bottom_b and \
           bottom_a > top_b:
            return True
        else:
            return False

    def collides_group(self, group, x=None, y=None):
        x, y = self._check_bounds(x, y)

        collisions = []
        entities = PC.room.get_group(group)
        for entity in entities:
            if entity is not self and entity.active and \
               self.collides(entity, x, y) and entity not in collisions:
                collisions.append(entity)
        return collisions
    
    def collides_groups(self, x, y, *groups):
        # TODO convert to *args
        x, y = self._check_bounds(x, y)

        collisions = []
        entities = []
        for group in groups:
            entities += PC.room.get_group(group)

        for entity in entities:
            if entity is not self and entity.active and \
               self.collides(entity, x, y) and entity not in collisions:
                collisions.append(entity)
        return collisions
    
    def collides_name(self, name, x=None, y=None):
        x, y = self._check_bounds(x, y)

        for entity in PC.room.entities:
            if entity.name == name and self.collides(entity, x, y):
                return entity
        return None

    def collides_point(self, point, x=None, y=None):
        x, y = self._check_bounds(x, y)

        px, py = point
        if x <= px <= x + self.width and y <= py <= y + self.height:
            return True
        else:
            return False

    def collides_rect(self, rect, x=None, y=None):
        x, y = self._check_bounds(x, y)

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
        x, y = self._check_bounds(x, y)

        collisions = []
        for entity in PC.room.entities:
            if entity == self or not entity.active:
                continue
            elif entity.solid and self.collides(entity, x, y):
                collisions.append(entity)
        return collisions
    
    def distance_from(self, entity):
        return abs((self.x - entity.x) + (self.y - entity.y))
    
    def member_of(self, group):
        for g in self.group:
            if group == g:
                return True
        return False

    def render(self):
        return
            
    def update(self):
        return


class EntityRoom(object):
    """
    Entity container
    """

    def __init__(self):
        self.entities = []

    def add(self, entity):
        self.entities.append(entity)
        return entity

    def clear(self):
        del self.entities[:]

    def get_group(self, group):
        ents = []
        for e in self.entities:
            if e.member_of(group):
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

    def __init__(self, world, name):
        self.world = world
        self.name = name

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
    State machine
    """

    def __init__(self):
        self.states = {}
        self.current_state = None

    def change_state(self, state_name, *args):
        if state_name in self.states and \
           state_name != self.current_state.name:
            previous_state = self.current_state
            incoming_state = self.states[state_name]

            previous_state.exit(incoming_state, *args)
            incoming_state.enter(previous_state, *args)
            
            self.current_state = incoming_state
        else:
            print state_name in self.states
            print '[ERROR] change_state request invalid'

    def exit(self):
        PC.room.clear()
        if self.current_state is not None:
            self.current_state.exit(None)

    def update(self):
        PC.room.update()

    def render(self):
        PC.room.render()


