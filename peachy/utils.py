import os
import pygame
from pygame.locals import *

import peachy
from peachy import DEBUG

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        if isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]


class Counter(object):
    def __init__(self, start, target, step=1, repeat=False, reverse=False):
        self.start = start
        self.target = target
        self.step = step
        self.current = start

        self.finished = False
        self.repeat = repeat
        self._reverse = reverse

    def complete(self):
        self.current = self.target
        self.finished = True

    def reset(self):
        self.current = self.start
        self.finished = False

    def reverse(self):
        t = self.start
        self.start = self.target
        self.target = t
        self.step *= -1

    def advance(self):
        self.tick()
        return self.finished

    def tick(self):
        if not self.finished:
            self.current += self.step
            self.current = round(self.current, 2)
            if self.current == self.target:  # TODO allow for over shooting target
                if self._reverse:
                    self.reverse()
                elif self.repeat:
                    self.current = 0
                else:
                    self.finished = True
            return self.current
        else:
            return False


class Camera(object):

    def __init__(self, view_width, view_height, speed=1):
        self.x = 0
        self.y = 0

        self.view_width = view_width
        self.view_height = view_height
        self.max_width = -1
        self.max_height = -1

        self.speed = speed
        self.target_x = 0
        self.target_y = 0

    def snap(self, target_x, target_y, center=False):
        self.snap_x(target_x, center)
        self.snap_y(target_y, center)

    def snap_x(self, target_x, center=False):
        if center:
            target_x -= self.view_width / 2
        self.x = target_x
        if self.x < 0:
            self.x = 0
        elif self.x + self.view_width > self.max_width:
            self.x = self.max_width - self.view_width

    def snap_y(self, target_y, center=False):
        if center:
            target_y -= self.view_height / 2
        self.y = target_y
        if self.y < 0:
            self.y = 0
        elif self.y + self.view_height > self.max_height:
            self.y = self.max_height - self.view_height

    def pan(self, target_x, target_y, center=False):
        self.pan_x(target_x, center)
        self.pan_y(target_y, center)

    def pan_x(self, target_x, center=False, speed=None):
        if speed is None:
            speed = self.speed
        if center:
            target_x -= self.view_width / 2

        if target_x < 0:
            target_x = 0
        elif target_x + self.view_width > self.max_width:
            target_x = self.max_width - self.view_width

        if self.x + speed < target_x:
            self.x += speed
        elif self.x - speed > target_x:
            self.x -= speed
        else:
            self.x = target_x

    def pan_y(self, target_y, center=False, speed=None):
        if speed is None:
            speed = self.speed
        if center:
            target_y -= self.view_height / 2

        if target_y < 0:
            target_y = 0
        elif target_y + self.view_height > self.max_height:
            target_y = self.max_height - self.view_height

        if self.y + speed < target_y:
            self.y += speed
        elif self.y - speed > target_y:
            self.y -= speed
        else:
            self.y = target_y

    def translate(self):
        peachy.graphics.translate(self.x, self.y)

class Mouse(object):
    """ Mouse input & tracking """
    current_state = (False, False, False)
    previous_state = (False, False, False)
    x = 0
    y = 0
    location = (0, 0)

    @staticmethod
    def init():
        Mouse.current_state = pygame.mouse.get_pressed()
        Mouse.previous_state = pygame.mouse.get_pressed()

    @staticmethod
    def down(button):
        code = Mouse._get_button_code(button)
        if code != -1:
            return Mouse.current_state[code]
        return False

    @staticmethod
    def pressed(button):
        code = Mouse._get_button_code(button)
        if code != -1:
            return Mouse.current_state[code] and not Mouse.previous_state[code]
        return False

    @staticmethod
    def released(button):
        code = Mouse._get_button_code(button)
        if code != -1:
            return not Mouse.current_state[code] and Mouse.previous_state[code]
        return False

    @staticmethod
    def _poll():
        Mouse.previous_state = Mouse.current_state
        Mouse.current_state = pygame.mouse.get_pressed()
        Mouse.x, Mouse.y = Mouse.location = pygame.mouse.get_pos()

    @staticmethod
    def _get_button_code(button):
        if button == 'left': return 0
        if button == 'right': return 2
        if button == 'middle' or button == 'center': return 1
        return -1

class Keys(object):
    """ Keyboard & Mouse input helper """

    current_state = []
    previous_state = []

    @staticmethod
    def init():
        Keys.current_state = pygame.key.get_pressed()
        Keys.previous_state = pygame.key.get_pressed()

    @staticmethod
    def down(key):
        code = Keys._get_key_code(key)
        if code != -1:
            return Keys.current_state[code]
        return False

    @staticmethod
    def pressed(key):
        if key == 'any':
            for code in xrange(len(Keys.current_state)):
                if Keys.current_state[code] and not Keys.previous_state[code]:
                    return True
            return False
        else:
            code = Keys._get_key_code(key)
            if code != -1:
                return Keys.current_state[code] and not Keys.previous_state[code]
            return False

    @staticmethod
    def released(key):
        code = Keys._get_key_code(key)
        if code != -1:
            return not Keys.current_state[code] and Keys.previous_state[code]
        return False

    @staticmethod
    def _poll():
        Keys.previous_state = Keys.current_state
        Keys.current_state = pygame.key.get_pressed()

    @staticmethod
    def _get_key_code(key):
        if key == 'enter':
            return K_RETURN
        elif key == 'escape':
            return K_ESCAPE
        elif key == 'lshift':
            return K_LSHIFT
        elif key == 'rshift':
            return K_RSHIFT
        elif key == 'space' or key == ' ':
            return K_SPACE
        elif key == 'left':
            return K_LEFT
        elif key == 'right':
            return K_RIGHT
        elif key == 'up':
            return K_UP
        elif key == 'down':
            return K_DOWN
        elif key == 'backspace':
            return K_BACKSPACE
        elif key == 'delete':
            return K_DELETE
        elif key == 'tab':
            return K_TAB

        elif key == '1':
            return K_1;
        elif key == '2':
            return K_2;
        elif key == '3':
            return K_3;
        elif key == '4':
            return K_4;
        elif key == '5':
            return K_5;
        elif key == '6':
            return K_6;
        elif key == '7':
            return K_7;
        elif key == '8':
            return K_8;
        elif key == '9':
            return K_9;
        elif key == '0':
            return K_0;

        elif key == 'F1':
            return K_F1;
        elif key == 'F2':
            return K_F2;
        elif key == 'F3':
            return K_F3;
        elif key == 'F4':
            return K_F4;
        elif key == 'F5':
            return K_F5;
        elif key == 'F6':
            return K_F6;
        elif key == 'F7':
            return K_F7;
        elif key == 'F8':
            return K_F8;
        elif key == 'F9':
            return K_F9;
        elif key == 'F10':
            return K_F10;
        elif key == 'F11':
            return K_F11;
        elif key == 'F12':
            return K_F12;

        elif key == '+':
            return K_KP_PLUS
        elif key == '-':
            return K_KP_MINUS
        elif key == '_':
            return K_UNDERSCORE
        elif key == '.':
            return K_PERIOD

        elif key == 'a':
            return K_a
        elif key == 'b':
            return K_b
        elif key == 'c':
            return K_c
        elif key == 'd':
            return K_d
        elif key == 'e':
            return K_e
        elif key == 'f':
            return K_f
        elif key == 'g':
            return K_g
        elif key == 'h':
            return K_h
        elif key == 'i':
            return K_i
        elif key == 'j':
            return K_j
        elif key == 'k':
            return K_k
        elif key == 'l':
            return K_l
        elif key == 'm':
            return K_m
        elif key == 'n':
            return K_n
        elif key == 'o':
            return K_o
        elif key == 'p':
            return K_p
        elif key == 'q':
            return K_q
        elif key == 'r':
            return K_r
        elif key == 's':
            return K_s
        elif key == 't':
            return K_t
        elif key == 'u':
            return K_u
        elif key == 'v':
            return K_v
        elif key == 'w':
            return K_w
        elif key == 'x':
            return K_x
        elif key == 'y':
            return K_y
        elif key == 'z':
            return K_z
        else:
            return -1


class TypeWriter(object):
    """
    The typewriter takes all alphanumeric input recorded by Keys and stores it
    inside of self.value. This is useful for text input like naming things.
    """

    def __init__(self, value=''):
        self.value = value

    def update(self):
        keys = [
            '1','2','3','4','5','6','7','8','9','0','.','_','-',
            'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',
            'r','s','t','u','v','w','x','y','z',
            'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q',
            'R','S','T','U','V','W','X','Y','Z', ' '
        ]

        shift = Keys.down('lshift') or Keys.down('rshift')

        if Keys.pressed('backspace') or Keys.pressed('delete'):
            self.value = self.value[:-1]

        for key in keys:
            if Keys.pressed(key):
                if shift:
                    self.value += key.upper()
                else:
                    self.value += key
