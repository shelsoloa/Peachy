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
    def __init__(self, start, target, step=1):
        self.start = start
        self.target = target
        self.step = step

        self.current = start
        self.finished = False

    def complete(self):
        self.current = self.target
        self.finished = True

    def reset(self):
        self.current = self.start
        self.finished = False

    def advance(self):
        self.tick()
        return self.finished

    def tick(self):
        if not self.finished:
            self.current += self.step
            if self.current == self.target:  # TODO allow for over shooting target
                self.finished = True
        return self.current


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


class Input(object):

    curr_key_state = []
    prev_key_state = []

    @staticmethod
    def init():
        Input.curr_key_state = pygame.key.get_pressed()
        Input.prev_key_state = pygame.key.get_pressed()

    @staticmethod
    def down(key):
        code = Input.get_key_code(key)
        if code != -1:
            return Input.curr_key_state[code]
        return False

    @staticmethod
    def pressed(key):
        if key == 'any':
            for code in xrange(len(Input.curr_key_state)):
                if Input.curr_key_state[code] and not Input.prev_key_state[code]:
                    return True
            return False
        else:
            code = Input.get_key_code(key)
            if code != -1:
                return Input.curr_key_state[code] and not Input.prev_key_state[code]
            return False
    
    @staticmethod
    def released(key):
        code = Input.get_key_code(key)
        if code != -1:
            return not Input.curr_key_state[code] and Input.prev_key_state[code]
        return False

    @staticmethod
    def poll_keyboard():
        Input.prev_key_state = Input.curr_key_state
        Input.curr_key_state = pygame.key.get_pressed()
    
    @staticmethod
    def get_key_code(key):
        if key == 'enter': 
            return K_RETURN
        elif key == 'escape': 
            return K_ESCAPE
        elif key == 'lshift': 
            return K_LSHIFT
        elif key == 'rshift': 
            return K_RSHIFT
        elif key == 'space': 
            return K_SPACE
        elif key == 'left': 
            return K_LEFT
        elif key == 'right': 
            return K_RIGHT
        elif key == 'up': 
            return K_UP
        elif key == 'down': 
            return K_DOWN

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

