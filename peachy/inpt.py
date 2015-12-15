import pygame
from pygame.locals import *

class mouse:
    x = 0
    y = 0

curr_key_state = []  # Possibly change to one array where index 0 is current
prev_key_state = []  # and index 1 is previous

# joystick = []
# joystick_raw = []

def down(key):
    code = get_key_code(key)
    if code != -1:
        return curr_key_state[code]
    return False

def get_key_code(key):
    key_low = key.lower()
    if key_low == 'enter':
        return K_RETURN
    elif key_low == 'escape':
        return K_ESCAPE
    elif key_low == 'lshift':
        return K_LSHIFT
    elif key_low == 'space':
        return K_SPACE
    elif key_low == 'left':
        return K_LEFT
    elif key_low == 'right':
        return K_RIGHT
    elif key_low == 'up':
        return K_UP
    elif key_low == 'down':
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

def poll():
    # poll_joystick()
    poll_keyboard()
    poll_mouse()

def poll_joysticks():
    # TODO Must supress all output due to an annoying bug in pygame where 
    # SDL will print SDL_GET_BUTTON_XXX, everytime this method is called.

    old_out = sys.stdout
    old_err = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    for joy_i in range(len(Input.joystick_raw)):

        joy_raw = Input.joystick_raw[joy_i]
        joystick = Input.joystick[joy_i]

        axes = []
        axis_count = joy_raw.get_numaxes()
        for axis_i in range(axis_count):
            axis = joy_raw.get_axis(axis_i)
            axes.append(axis)
        joystick['AXIS'] = axes

        buttons = []
        button_count = joy_raw.get_numbuttons()
        for button_i in range(button_count):
            button = joy_raw.get_button(button_i)
            buttons.append(button)
        joystick['BUTTON'] = button

    sys.stdout.close()
    sys.stderr.close()
    sys.stdout = old_out
    sys.stderr = old_err

def poll_keyboard():
    global curr_key_state
    global prev_key_state

    prev_key_state = curr_key_state
    curr_key_state = pygame.key.get_pressed()

    # Joystick control is currently unavailable
    # if len(joystick_raw) > 0:
    #    poll_joysticks()

def poll_mouse():
    # global curr_mouse_state
    # global prev_mouse_state

    mouse.x, mouse.y = pygame.mouse.get_pos()
    # prev_mouse_state = curr_mouse_state
    # curr_mouse_state = pygame.mouse.get_pressed()

def pressed(key):
    if key == 'ANY':
        for code in range(len(Input.curr_key_state)):
            if Input.curr_key_state[code] and not Input.prev_key_state[code]:
                return True
        return False
    elif key[:3] == 'JOY':
        return False
        # TODO add functionality for custom axes

        if len(joystick) > 0:
            joystick = joystick[0]

        code = key[4:]
        if code == 'UP':
            return False
        elif code == 'DOWN':
            return False
        elif code == 'LEFT':
            return False
        elif code == 'RIGHT':
            return False
        elif key[4:10] == 'BUTTON':
            result = False
            try:
                code = int(key[10:])
                result = joystick['BUTTON'][code] == 0
            except ValueError:
                if __debug__:
                    print 'Cannot recognize JOY_BUTTON: {}'.format(key[10:])
            except IndexError:
                if __debug__:
                    print 'Invalid JOY_BUTTON index: {}'.format(code)
            return result

    else:
        code = Input.get_key_code(key)
        if code != -1:
            return Input.curr_key_state[code] and not Input.prev_key_state[code]
        else:
            return False

def released(key):
    code = Input.get_key_code(key)
    if code != -1:
        return not Input.curr_key_state[code] and Input.prev_key_state[code]
    else:
        return False
