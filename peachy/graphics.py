"""Peachy Graphics module
"""
import math

import pygame
from pygame import Surface
from pygame import gfxdraw
from pygame.freetype import Font

from peachy.geo import Point

FLIP_X = 0x01
FLIP_Y = 0x02

_default_context = None
_context = None
_context_rect = None
_context_stack = []

_translation = Point()

_color = pygame.Color(0, 0, 0)
_font = None


# Drawing


def draw(image, x, y, args=0):
    """Draw an image to the current context

    Args:
        image (Surface): A Surface object to render to the context
        x (int): The x-coordinate to render the image at.
        y (int): The y-coordinate to render the image at.
    """
    x -= _translation.x
    y -= _translation.y

    bounds = image.get_rect().move(x, y)

    if bounds.colliderect(_context_rect):
        if args & FLIP_X:
            image = pygame.transform.flip(image, True, False)
        if args & FLIP_Y:
            image = pygame.transform.flip(image, False, True)

        _context.blit(image, (x, y))


def draw_arc(x, y, r, start, end):
    alpha = False
    try:
        alpha = _color[3] < 255
    except IndexError:
        alpha = False

    if not alpha:
        x = int(x - _translation.x)
        y = int(y - _translation.y)

    points = []
    points.append((x, y))
    for angle in range(start, end):
        rad = math.radians(angle)
        dx = math.cos(rad) * r
        dy = math.cos(rad) * r
        points.append((x + dx, y + dy))

    if alpha:
        draw_polygon(points)
    else:
        pygame.draw.polygon(_context, _color, points)


def draw_entity_rect(entity):
    draw_rect(entity.x, entity.y, entity.width, entity.height)


def draw_circle(x, y, r):
    x = int(x - _translation.x + r)
    y = int(y - _translation.y + r)

    try:
        assert _color[3] < 255
        temp = Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp, _color, (r, r), r)
        _context.blit(temp, (x - r, y - r))
    except (AssertionError, IndexError):
        pygame.draw.circle(_context, _color, (x, y), r)


def draw_line(x1, y1, x2, y2):
    x1 -= _translation.x
    x2 -= _translation.x
    y1 -= _translation.y
    y2 -= _translation.y

    pygame.draw.line(_context, _color, (x1, y1), (x2, y2))


def draw_polygon(points, aa=False):
    if aa:
        gfxdraw.filled_polygon(_context, points, _color)
        gfxdraw.aapolygon(_context, points, _color)
    else:
        temp = Surface((_context.get_width(), _context.get_height()),
                       pygame.SRCALPHA)
        pygame.draw.polygon(temp, _color, points)
        _context.blit(temp, (-_translation.x, -_translation.y))


def draw_rect(x, y, width, height, thickness=0):
    """ Draw a rectangle """
    x -= _translation.x
    y -= _translation.y

    try:
        assert _color[3] < 255
        temp = Surface((width, height), pygame.SRCALPHA)
        if thickness <= 0:
            temp.fill(_color)
        else:
            pygame.draw.rect(temp, _color, (0, 0, width, height), thickness)
        _context.blit(temp, (x, y))
    except (AssertionError, IndexError):
        pygame.draw.rect(_context, _color, (x, y, width, height), thickness)


def draw_rounded_rect(x, y, width, height, radius):
    """ Draw a rectangle with rounded corners """
    rect = pygame.Rect(x, y, width, height)
    color = pygame.Color(*_color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = (0, 0)
    rectangle = Surface(rect.size, pygame.SRCALPHA)

    circle = Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle,
                                          [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    _context.blit(rectangle, pos)


def draw_text(text, x, y, aa=True, center=False, font=None):
    if font:
        text_surface, text_rect = font.render(text, _color)
    else:
        text_surface, text_rect = _font.render(text, _color)
    text_rect.x = x - _translation.x
    text_rect.y = y - _translation.y

    if center:
        text_rect.centerx = _context_rect.centerx

    _context.blit(text_surface, text_rect)


""" State Modification """
# TODO Only apply transformations to current context and sub-contexts


def font():
    return _font


def pop_context():
    """ Revert to the previous graphics context """
    global _context_stack

    # retrieve the last context stashed
    # Note:
    try:
        set_context(_context_stack.pop())
    except IndexError:
        set_context(_default_context)


def push_context(context_surface):
    """
    Set a Surface as the current graphics context.

    Undo this operation by using pop_context() or reset_context()
    """

    # Context's are stashed inside the context_stack only when a new context has
    # been pushed onto the stack. IE. The current context is not stored in
    # context_stack.

    global _context_stack

    # stash previous context inside context_stack
    _context_stack.append(_context)

    # set current context
    set_context(context_surface)


def reset_context():
    """
    Reset to the default context.
    Clears context stack and translations.
    """

    global _context_stack
    global _translation

    set_context(_default_context)
    _context_stack.clear()

    _translation.x = 0
    _translation.y = 0


def rgb_to_hex(color):
    return '%02x%02x%02x' % (color.r, color.g, color.b)


def set_color(r, g, b, a=255):
    global _color

    if (0 <= r <= 255) and \
       (0 <= g <= 255) and \
       (0 <= b <= 255) and \
       (0 <= a <= 255):
        # TODO fix alpha
        _color = pygame.Color(r, g, b, a)


def set_color_hex(val):
    # (#ffffff) -> (255, 255, 255)
    val = val.lstrip('#')
    lv = len(val)
    # Hell if I know how this works... Thanks Stack Overflow
    _color = tuple(int(val[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    set_color(*_color)


def set_context(new_context):
    global _context
    global _context_rect

    _context = new_context
    _context_rect = new_context.get_rect()


def set_default_context(default_context):
    global _default_context
    _default_context = default_context


def set_font(new_font):
    global _font
    _font = new_font


def translate(x, y, absolute=True):
    global _translation

    if absolute:
        _translation.x = x
        _translation.y = y
    else:
        _translation.x += x
        _translation.y += y


""" Image Manip """


def flip(image, x, y):
    return pygame.transform.flip(image, x, y)


def rotate(image, degree):
    return pygame.transform.rotate(image, degree)


def scale(image, scale, dest=None):
    x, y, w, h = image.get_rect()
    if dest is not None:
        pygame.transform.scale(image, (w * scale, h * scale), dest)
    else:
        return pygame.transform.scale(image, (w * scale, h * scale))


def splice(image, frame_width, frame_height, margin_x=0, margin_y=0):
    # Arguments: image is of pygame.Surface
    x = 0
    y = 0

    sub_images = []

    src_width, src_height = image.get_size()

    while x + frame_width <= src_width and y + frame_height <= src_height:
        crop = Surface((frame_width, frame_height), flags=pygame.SRCALPHA)
        crop.blit(image, (0, 0), (x, y, frame_width, frame_height))

        sub_images.append(crop)

        x += frame_width + margin_x
        if x + frame_width > src_width:
            x = 0
            y += frame_height + margin_y

    return sub_images


class Context(object):
    def __init__(self, width=0, height=0, x=0, y=0, surface=None):
        # TODO attempt to make hardware surface first
        # TODO check SDL_video.h
        if surface is None:
            self.surface = pygame.Surface(width, height)
            self.width = width
            self.height = height
        else:
            self.surface = surface
            self.width = surface.get_width()
            self.height = surface.get_height()
        self.x = x
        self.y = y
        self.transformations = []

    def resize(self, width, height):
        # TODO check for memory leaks
        self.surface = pygame.Surface(width, height)
        self.width = width
        self.height = height


class SpriteMap(object):

    def __init__(self, source, frame_width, frame_height,
                 margin=(0, 0), origin=(0, 0)):
        self.source = source

        self.name = ''
        self.flipped_x = False
        self.flipped_y = False
        self.paused = False

        self.animations = dict()
        self.frames = []

        self.current_animation = None
        self.current_frame = -1
        self.time_remaining = 0
        self.reversing = False
        self.callback = None

        self.frames = splice(source, frame_width, frame_height,
                             margin[0], margin[1])
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.origin = Point(origin[0], origin[1])

    def add(self, name, frames, frame_rate=0, loops=False, pingpongs=False,
            origin=None, callback=None):
        if origin is None and self.origin is not None:
            origin = (self.origin.x, self.origin.y)

        animation = {
            "frames": frames,
            "frame_rate": frame_rate,
            "loops": loops,
            "pingpongs": pingpongs,
            "callback": callback,
            "origin": origin
        }
        self.animations[name] = animation

    def pause(self):
        self.paused = True

    def play(self, anim_name, flip_x=False, flip_y=False, restart=False):
        """
        Play the animation specified by anim_name.
        flip along x or y axis by specifying flip_x and flip_y
        restart will start the animation for the very beginning
        """
        if anim_name in self.animations:
            if self.name != anim_name or \
               self.flipped_x != flip_x or \
               self.flipped_y != flip_y or \
               restart:
                self.name = anim_name
                self.flipped_x = flip_x
                self.flipped_y = flip_y
                self.paused = False

                self.current_animation = self.animations[anim_name]
                self.current_frame = 0
                self.reversing = False
                self.time_remaining = self.current_animation['frame_rate']
                self.callback = self.current_animation['callback']

    def render(self, x, y):
        if not self.paused:
            self.step()

        x -= self.current_animation['origin'][0]
        y -= self.current_animation['origin'][1]

        frame = self.current_animation['frames'][self.current_frame]
        args = 0

        if frame != -1:
            if self.flipped_x:
                args = args | FLIP_X
            if self.flipped_y:
                args = args | FLIP_Y
            draw(self.frames[frame], x, y, args)

    def resume(self):
        self.paused = False

    def step(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1

            if self.time_remaining <= 0:

                animation_complete = False
                if self.reversing:
                    self.current_frame -= 1
                    if self.current_frame < 1:
                        animation_complete = True
                else:
                    self.current_frame += 1
                    if self.current_frame >= \
                       len(self.current_animation['frames']):
                        animation_complete = True

                if animation_complete:

                    # Loop or not

                    if not self.reversing and \
                       self.current_animation['pingpongs']:
                        self.current_frame -= 2
                        self.reversing = True
                        self.time_remaining = \
                            self.current_animation['frame_rate']
                    elif self.current_animation['loops']:
                        self.current_frame = 0
                        self.time_remaining = \
                            self.current_animation['frame_rate']
                        self.reversing = False
                    else:
                        self.current_frame -= 1
                        self.time_remaining = 0
                        if self.callback is not None:
                            self.callback()
                else:
                    self.time_remaining = self.current_animation['frame_rate']

    def stop(self):
        self.paused = True
        self.current_frame = 0
        self.time_remaining = self.current_animation['frame_rate']
