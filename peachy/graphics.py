import os
import pygame

from pygame import Surface
from pygame import gfxdraw
from pygame.freetype import Font

from peachy import PC
from peachy.utils import Point

FLIP_X = 0x01
FLIP_Y = 0x02

DEFAULT_CONTEXT = None  # A constant that holds the main render context

__context = None
__context_rect = None
__translation = Point()

__color = pygame.Color(0, 0, 0)
__font = None

""" Drawing """

def draw(image, x, y, args=0):
    x -= __translation.x
    y -= __translation.y
    
    bounds = image.get_rect().move(x, y)

    if bounds.colliderect(__context_rect):
        if args & FLIP_X:
            image = pygame.transform.flip(image, True, False)
        if args & FLIP_Y:
            image = pygame.transform.flip(image, False, True)

        __context.blit(image, (x, y))

def draw_arc(x, y, r, start, end):
    alpha = False
    try:
        alpha = __color[3] < 255
    except IndexError:
        alpha = False

    if not alpha:
        x = int(x - __translation.x)
        y = int(y - __translation.y)

    points = []
    points.append((x, y))
    for angle in xrange(start, end):
        rad = math.radians(angle)
        dx = math.cos(rad) * r
        dy = math.cos(rad) * r
        points.append((x + dx, y + dy))

    if alpha:
        draw_polygon(points)
    else:
        pygame.draw.polygon(__context, __color, points)

def draw_entity_rect(entity):
    draw_rect(entity.x, entity.y, entity.width, entity.height)

def draw_circle(x, y, r):
    x = int(x - __translation.x + r)
    y = int(y - __translation.y + r)

    try:
        assert __color[3] < 255
        temp = Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp, __color, (r, r), r)
        __context.blit(temp, (x - r, y - r))
    except (AssertionError, IndexError):
        pygame.draw.circle(__context, __color, (x, y), r)

def draw_line(x1, y1, x2, y2):
    x1 -= __translation.x
    x2 -= __translation.x
    y1 -= __translation.y
    y2 -= __translation.y

    pygame.draw.line(__context, __color, (x1, y1), (x2, y2))

def draw_polygon(points, aa=False):
    if aa:
        gfxdraw.filled_polygon(__context, points, __color)
        gfxdraw.aapolygon(__context, points, __color)
    else:
        temp = Surface((__context.get_width(), __context.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(temp, __color, points)
        __context.blit(temp, (-__translation.x, -__translation.y))


def draw_rect(x, y, width, height):
    """ Draw a rectangle """
    x -= __translation.x
    y -= __translation.y

    try:
        assert __color[3] < 255
        temp = Surface((width, height), pygame.SRCALPHA)
        temp.fill(__color)
        __context.blit(temp, (x, y))
    except (AssertionError, IndexError):
        pygame.draw.rect(__context, __color, (x, y, width, height))

def draw_rounded_rect(x, y, width, height, radius):
    """ Draw a rectangle with rounded corners """
    rect = pygame.Rect(x, y, width, height)
    color = pygame.Color(*__color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = (0, 0)
    rectangle = Surface(rect.size, pygame.SRCALPHA)

    circle = Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)
    
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

    __context.blit(rectangle, pos)

def draw_text(text, x, y, aa=True, center=False, font=None):
    if font:
        text_surface, text_rect = font.render(text, __color)
    else:
        text_surface, text_rect = __font.render(text, __color)
    text_rect.x = x - __translation.x
    text_rect.y = y - __translation.y

    if center:
        text_rect.centerx = __context_rect.centerx

    __context.blit(text_surface, text_rect)


""" State Modification """
# TODO Only apply transformations to current context and subcontexts

def font():
    return __font

def reset_context():
    global __context
    global __context_rect
    global __translation

    __context = DEFAULT_CONTEXT
    __context_rect = DEFAULT_CONTEXT.get_rect()
    __translation.x = 0
    __translation.y = 0

def rgb_to_hex(color):
    return '%02x%02x%02x' % (color.r, color.g, color.b)

def set_color(r, g, b, a=255):
    global __color

    if (0 <= r <= 255) and (0 <= g <= 255) and (0 <= b <= 255) and (0 <= a <= 255):
        # TODO fix alpha
        __color = pygame.Color(r, g, b, a)

def set_color_hex(val):
    # (#ffffff) -> (255, 255, 255)
    val = val.lstrip('#')
    lv = len(val)
    # Hell if I know how this works... Thanks Stack Overflow
    __color = tuple(int(val[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    set_color(*__color)

def set_context(new_context):
    global __context
    global __context_rect

    __context = new_context
    __context_rect = __context.get_rect()

def set_font(new_font):
    global __font
    __font = new_font

def translate(x, y, absolute=True):
    global __translation

    if absolute:
        __translation.x = x
        __translation.y = y
    else:
        __translation.x += x
        __translation.y += y

""" Image Manip """

def rotate(image, degree):
    return pygame.transform.rotate(image, degree)

def scale(image, scale):
    x, y, w, h = image.get_rect()
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

class SpriteMap(object):

    def __init__(self, source, frame_width, frame_height, margin_x=0, margin_y=0, origin_x=0, origin_y=0):
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

        self.callback = None

        self.frames = splice(source, frame_width, frame_height, margin_x, margin_y)
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.origin = Point(origin_x, origin_y)
        # self.origin_x = origin_x
        # self.origin_y = origin_y

    def add(self, name, frames, frame_rate=0, loops=False, callback=None, origin=(0,0)):
        animation = {
            "frames": frames,
            "frame_rate": frame_rate,
            "loops": loops,
            "callback": callback,
            "origin": origin
        }
        self.animations[name] = animation

    def pause(self):
        self.paused = True

    """
    Will play the animation specified by anim_name.
    flip_x and flip_y will flip along the x or y axis respectively
    restart will start the animation for the very beginning
    """
    def play(self, anim_name, flip_x=False, flip_y=False, restart=False):
        if anim_name in self.animations:
            if self.name != anim_name or self.flipped_x != flip_x or \
               self.flipped_y != flip_y or restart:
                self.name = anim_name
                self.flipped_x = flip_x
                self.flipped_y = flip_y
                self.paused = False

                self.current_animation = self.animations[anim_name]
                self.current_frame = 0
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
                self.current_frame += 1

                if self.current_frame >= len(self.current_animation['frames']):

                    # Loop or not
                    
                    if self.current_animation['loops']:
                        self.current_frame = 0
                        self.time_remaining = self.current_animation['frame_rate']
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

