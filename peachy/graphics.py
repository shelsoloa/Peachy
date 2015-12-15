import pygame

FLIP_X = 0x01
FLIP_Y = 0x02

_MAIN_CONTEXT = None  # A constant that holds the main render context

context = None
context_rect = None

color = pygame.Color(0, 0, 0)
font = None

translate_x = 0
translate_y = 0

def draw_image(image, x, y, args=0):
    x -= translate_x
    y -= translate_y
    
    bounds = image.get_rect().move(x, y)

    if bounds.colliderect(context_rect):
        if args & FLIP_X:
            image = pygame.transform.flip(image, True, False)
        if args & FLIP_Y:
            image = pygame.transform.flip(image, False, True)

        context.blit(image, (x, y))

def draw_line(x1, y1, x2, y2):
    x1 -= translate_x
    y1 -= translate_y
    x2 -= translate_x
    y2 -= translate_y

    pygame.draw.line(context, color, (x1, y1), (x2, y2))

def draw_circle(x, y, diameter):
    radius = diameter / 2

    x = int(x - translate_x + radius)
    y = int(y - translate_y + radius)

    pygame.draw.circle(context, color, (x, y), radius)

def draw_rect(x, y, width, height):
    x -= translate_x
    y -= translate_y
    
    pygame.draw.rect(context, color, (x, y, width, height))

def draw_text(text, x, y, aa=False, center=False):
    text_surface = font.render(text, aa, color)
    text_rect = text_surface.get_rect()
    text_rect.x = x - translate_x
    text_rect.y = y - translate_y

    if center:
        text_rect.centerx = context_rect.centerx

    context.blit(text_surface, text_rect)

def set_color(r, g, b, a=255):
    global color

    if (0 <= r <= 255) and (0 <= g <= 255) and (0 <= b <= 255) and (0 <= a <= 255):
        # TODO fix alpha
        color = pygame.Color(r, g, b, a)

def set_context(new_context):
    global context
    global context_rect

    context = new_context
    context_rect = context.get_rect()

def transform_rotate(image, degree):
    return pygame.transform.rotate(image, degree)

def translate(x, y):
    global translate_x
    global translate_y

    translate_x = x
    translate_y = y

def translate_center(x, y):
    global translate_x
    global translate_y

    half_vw, half_vh = [v / 2 for v in pc.view_size]
    translate_x = x - half_vw
    translate_y = y - half_vh


class Sprite(object):
    
    def __init__(self, source, origin_x=0, origin_y=0):
        self.source = source

        self.origin_x = origin_x
        self.origin_y = origin_y

        self.flipped_x = False
        self.flipped_y = False

    def render(self, x, y):
        x -= self.origin_x
        y -= self.origin_y

        args = 0

        if self.flipped_x:
            args = args | FLIP_X
        if self.flipped_y:
            args = args | FLIP_Y
        draw_image(self.source, x, y, args)


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

        self.frames = splice_image(source, frame_width, frame_height, margin_x, margin_y)
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.origin_x = origin_x
        self.origin_y = origin_y

    def add(self, name, frames, frame_rate=0, loops=False, callback=None):
        animation = {
            "frames": frames,
            "frame_rate": frame_rate,
            "loops": loops,
            "callback": callback
        }
        self.animations[name] = animation

    def pause(self):
        self.paused = True

    def play(self, anim_name, flip_x=False, flip_y=False):
        if anim_name in self.animations:
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

        x -= self.origin_x
        y -= self.origin_y

        frame = self.current_animation['frames'][self.current_frame]
        args = 0
        
        if frame != -1:
            if self.flipped_x:
                args = args | FLIP_X
            if self.flipped_y:
                args = args | FLIP_Y
            draw_image(self.frames[frame], x, y, args)

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

