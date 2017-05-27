"""Peachy utilities

Utility classes and functions.
"""

import logging
import pygame
import pygame.locals


def list_wrap(store):
    """Create copy of list to iterate over.
    This allows for operations to be performed on the copy while iterating.

    Example:
        Delete elements from an array while iterating through the array
        >>> item = [0, 1, 2]
        >>> for item in list_wrap(lst):
        >>>     # Do stuff with item
        >>>     lst.remove(item)

    Args:
        store (list): The list that will be wrapped

    Yields:
        object: The next object in the list.
    """
    wrapper = list(store)
    for item in wrapper:
        yield item


def dict_wrap(store):
    """The same as list_wrap but with dict instead."""
    wrapper = dict(store)
    for k, v in wrapper.items():
        yield k, v


class Counter(object):
    """Simple countdown helper

    Attributes:
        start (int): The number the counter starts at.
        target (int): The number the counter is counting to.
        current (int): The current count.
        step_increment (int): The amount to count by.
        repeat_enabled (bool): True if the counter repeats after completion.
        repeat_cap (int): The amount of times the counter repeats before
            stopping. If None then the counter repeats until explicitly stopped.
        repeat_count (int): The current repeat count (stops repeating after
            exceeding repeat_cap).
        pingpong_enabled (bool): Is pingponging enabled?
            IE: Pingponging is when the counter counts back to start after
                hitting target to complete cycle.
        reversed (bool): True if pingpong is active (counting back to start).
        allow_overshoot (bool): Can counter count over the target?
        complete (bool): Has counter reached target?
        callback (func): An optional callback function to be executed on
            completion.
        callback_args (list): A list of arguments to pass to callback function.
    """

    def __init__(self, start, target, step=1,
                 enable_pingpong=False, enable_repeat=False, repeat_cap=None,
                 allow_overshoot=False, callback=None, callback_args=None):
        """Initialize Counter.

        Args:
            start (int): The number to start counter at.
            target (int): The number to end counter at.
            step (int, optional): The increment to count by.
            enable_pingpong (bool, optional): Enable pingpong for this counter.
            enable_repeat (bool, optional): Enable repeating for this counter.
            repeat_cap (int, optional): The amount of times to repeat before
                flagging complete. Disabled by default (counter repeats until
                explicitly stopped).
            allow_overshoot (bool, optional): Enabled overshooting of target.
                IE: If self.current passes target, does it count as complete.
                Enabled by default.
            callback (func, optional): A callback function. Executed on
                completion.
            callback_args (list): A list of arguments to pass to callback
        """
        self.start = start
        self.target = target
        self.step_increment = step
        self.current = start

        self.repeat_enabled = enable_repeat
        self.repeat_cap = repeat_cap
        self.repeat_count = 1

        self.pingpong_enabled = enable_pingpong
        self.reversed = False

        self.allow_overshoot = allow_overshoot

        self.complete = False
        self.callback = callback
        self.callback_args = callback_args

    def advance(self):
        """Performs one step and checks for completion.

        If pingponging is enabled, this function will perform a reverse() after
        completing the original count.

        If repeating is enabled, this function will perform a reset() as soon
        as it hits the target.

        Returns:
            bool: True, if counter has completed
        """

        # I wrote out the possible cases(C) because writing this was confusing.
        # Hopefully this helps to understand what I did here
        #
        # C1 F Cycle not complete
        # C2 T Cycle complete, Ping disabled, Repeat disabled
        # C3 F Cycle complete, Ping disabled, Repeat enabled
        # C4 F Cycle complete, Ping enabled, Full not complete
        # C5 T Cycle complete, Ping enabled, Full complete, Repeat disabled
        # C6 F Cycle complete, Ping enabled, Full complete, Repeat enabled
        # C7 T Cycle is complete

        if self.complete:
            return True  # C7

        self._step()

        # If the cycle is not complete we can exit now
        # Case 1
        if not self._is_cycle_complete():
            return False

        # pingpong - Case 4, 5 and, 6
        if self.pingpong_enabled:
            if not self.reversed:
                # C4
                self.reverse()
                return False
            elif self.repeat_enabled:
                # C6
                self._repeat()
                return False
            else:
                # C5
                self._complete()
                return True
        # repeat - Case 3
        elif self.repeat_enabled:
            self._repeat()
            return False
        # complete - Case 2
        else:
            self._complete()
            return True

    def hard_reset(self):
        """Reset count, repeat_count, unreverse, and uncomplete."""
        self.repeat_count = 0
        self.complete = False
        self.reset()

    def reset(self):
        """Reset count and unreverse."""
        if self.reversed:
            self.reverse()
        self.current = self.start

    def reverse(self):
        """Reverses the Counter. start = target. target is start.
        Note: Does not change current
        """
        self.reversed = not self.reversed
        self.start, self.target = self.target, self.start
        self.step_increment *= -1

    def _complete(self):
        self.complete = True
        if callable(self.callback):
            self.callback(self.callback_args)

    def _is_cycle_complete(self):
        if not self.allow_overshoot:
            if self.step_increment > 0:
                return self.current >= self.target
            else:
                return self.current <= self.target
        else:
            return self.current == self.target

    def _repeat(self):
        if self.repeat_cap is not None:
            self.repeat_count += 1
            if self.repeat_count >= self.repeat_cap:
                self.repeat_enabled = False
        self.reset()

    def _step(self):
        self.current += self.step_increment


class Input(object):
    """Input handler

    Doesn't do much at the moment besides initializing and updating Key and
    Mouse.
    Used by peachy.Engine, you can safely ignore it.

    Todo:
        Add Joystick support
    """

    last_100 = None  # The last 100 keys pressed

    @staticmethod
    def init():
        """Initializes Keyboard, Mouse, and Joystick(TODO)."""
        Key.init()
        Mouse.init()
        # Joystick._poll()

    @staticmethod
    def poll():
        """Update Key, Mouse, and Joystick(TODO)"""
        Key._poll()
        Mouse._poll()
        # Joystick._poll()


class Key(object):
    """Keyboard input handler."""

    _current_state = []
    _previous_state = []

    # TODO add all pygame Key locals here.
    a = pygame.locals.K_a

    @staticmethod
    def init():
        Key._current_state = pygame.key.get_pressed()
        Key._previous_state = pygame.key.get_pressed()

    @staticmethod
    def down(key):
        """Check if 'key' is being held down.

        Args:
            key: a string (name of button) or pygame keycode.

        Returns:
            bool: True if 'key' is down.
        """

        code = Key._get_key_code(key)
        if code is not None:
            return Key._current_state[code]
        return False

    @staticmethod
    def pressed(key):
        """Check if 'key' has been pressed THIS cycle.

        Args:
            key: a string (name of button) or pygame keycode. Can also provide
                 "any" to survey if ANY KEY was pressed this cycle.

        Returns:
            bool: True if 'key' was pressed THIS cycle.
        """

        if key == 'any':
            for code in range(len(Key._current_state)):
                if Key._current_state[code] and not Key._previous_state[code]:
                    return True
            return False
        else:
            code = Key._get_key_code(key)
            if code is not None:
                return Key._current_state[code] and not \
                    Key._previous_state[code]
            return False

    @staticmethod
    def released(key):
        """Check if 'key' was released THIS cycle.

        Args:
            key: a string (name of button) or pygame keycode.

        Returns:
            bool: True if 'key' was released THIS cycle.
        """
        code = Key._get_key_code(key)
        if code is not None:
            return not Key._current_state[code] and Key._previous_state[code]
        return False

    @staticmethod
    def _poll():
        """Update Key state (called by peachy.Engine)"""
        Key._previous_state = Key._current_state
        Key._current_state = pygame.key.get_pressed()

    @staticmethod
    def _get_key_code(key):
        """Convert string to pygame keycode.

        If an integer is provided, then it is assumed that 'key' is already a
        keycode and is returned as is.

        Args:
            key: a string (name of button)

        Returns:
            int: pygame keycode associated to that key
        """

        if type(key) is int:
            return key
        elif key == 'enter':
            return pygame.locals.K_RETURN
        elif key == 'escape':
            return pygame.locals.K_ESCAPE
        elif key == 'lshift':
            return pygame.locals.K_LSHIFT
        elif key == 'rshift':
            return pygame.locals.K_RSHIFT
        elif key == 'space' or key == ' ':
            return pygame.locals.K_SPACE
        elif key == 'left':
            return pygame.locals.K_LEFT
        elif key == 'right':
            return pygame.locals.K_RIGHT
        elif key == 'up':
            return pygame.locals.K_UP
        elif key == 'down':
            return pygame.locals.K_DOWN
        elif key == 'backspace':
            return pygame.locals.K_BACKSPACE
        elif key == 'delete':
            return pygame.locals.K_DELETE
        elif key == 'tab':
            return pygame.locals.K_TAB

        elif key == '1':
            return pygame.locals.K_1
        elif key == '2':
            return pygame.locals.K_2
        elif key == '3':
            return pygame.locals.K_3
        elif key == '4':
            return pygame.locals.K_4
        elif key == '5':
            return pygame.locals.K_5
        elif key == '6':
            return pygame.locals.K_6
        elif key == '7':
            return pygame.locals.K_7
        elif key == '8':
            return pygame.locals.K_8
        elif key == '9':
            return pygame.locals.K_9
        elif key == '0':
            return pygame.locals.K_0

        elif key == 'F1':
            return pygame.locals.K_F1
        elif key == 'F2':
            return pygame.locals.K_F2
        elif key == 'F3':
            return pygame.locals.K_F3
        elif key == 'F4':
            return pygame.locals.K_F4
        elif key == 'F5':
            return pygame.locals.K_F5
        elif key == 'F6':
            return pygame.locals.K_F6
        elif key == 'F7':
            return pygame.locals.K_F7
        elif key == 'F8':
            return pygame.locals.K_F8
        elif key == 'F9':
            return pygame.locals.K_F9
        elif key == 'F10':
            return pygame.locals.K_F10
        elif key == 'F11':
            return pygame.locals.K_F11
        elif key == 'F12':
            return pygame.locals.K_F12

        elif key == '+':
            return pygame.locals.K_KP_PLUS
        elif key == '-':
            return pygame.locals.K_KP_MINUS
        elif key == '_':
            return pygame.locals.K_UNDERSCORE
        elif key == '.':
            return pygame.locals.K_PERIOD

        elif key == 'a':
            return pygame.locals.K_a
        elif key == 'b':
            return pygame.locals.K_b
        elif key == 'c':
            return pygame.locals.K_c
        elif key == 'd':
            return pygame.locals.K_d
        elif key == 'e':
            return pygame.locals.K_e
        elif key == 'f':
            return pygame.locals.K_f
        elif key == 'g':
            return pygame.locals.K_g
        elif key == 'h':
            return pygame.locals.K_h
        elif key == 'i':
            return pygame.locals.K_i
        elif key == 'j':
            return pygame.locals.K_j
        elif key == 'k':
            return pygame.locals.K_k
        elif key == 'l':
            return pygame.locals.K_l
        elif key == 'm':
            return pygame.locals.K_m
        elif key == 'n':
            return pygame.locals.K_n
        elif key == 'o':
            return pygame.locals.K_o
        elif key == 'p':
            return pygame.locals.K_p
        elif key == 'q':
            return pygame.locals.K_q
        elif key == 'r':
            return pygame.locals.K_r
        elif key == 's':
            return pygame.locals.K_s
        elif key == 't':
            return pygame.locals.K_t
        elif key == 'u':
            return pygame.locals.K_u
        elif key == 'v':
            return pygame.locals.K_v
        elif key == 'w':
            return pygame.locals.K_w
        elif key == 'x':
            return pygame.locals.K_x
        elif key == 'y':
            return pygame.locals.K_y
        elif key == 'z':
            return pygame.locals.K_z
        else:
            return None


class Mouse(object):
    """Mouse input & tracking handler."""
    _current_state = (False, False, False)
    _previous_state = (False, False, False)
    x = 0
    y = 0
    location = (0, 0)

    @staticmethod
    def init():
        Mouse._current_state = pygame.mouse.get_pressed()
        Mouse._previous_state = pygame.mouse.get_pressed()

    @staticmethod
    def down(button):
        """Check if button is being held down.

        Args:
            button: name or number of button.

        Returns:
            bool: True if button is down.
        """
        code = Mouse._get_button_code(button)
        if code != -1:
            return Mouse._current_state[code]
        return False

    @staticmethod
    def pressed(button):
        """Check if button was clicked THIS cycle

        Args:
            button: name or number of button.

        Returns:
            bool: True if button was clicked THIS cycle.
        """

        code = Mouse._get_button_code(button)
        if code != -1:
            return Mouse._current_state[code] and \
                not Mouse._previous_state[code]
        return False

    @staticmethod
    def released(button):
        """Check if button was released THIS cycle

        Args:
            button: name or number of button.

        Returns:
            bool: True if button was released THIS cycle.
         """
        code = Mouse._get_button_code(button)
        if code != -1:
            return not Mouse._current_state[code] and \
                Mouse._previous_state[code]
        return False

    # TODO
    # def double_click(button)

    @staticmethod
    def _poll():
        """ Update Mouse state (called by peachy.Engine) """
        Mouse._previous_state = Mouse._current_state
        Mouse._current_state = pygame.mouse.get_pressed()
        Mouse.x, Mouse.y = Mouse.location = pygame.mouse.get_pos()

    @staticmethod
    def _get_button_code(button):
        """
        Convert 'button' string to buttoncode.
        If an integer is provided, then it is assumed that 'button' is already a
        buttoncode and is returned as is.
        """
        if type(button) is int:
            return button
        elif button == 'left':
            return 0
        elif button == 'right':
            return 2
        elif button == 'middle' or button == 'center':
            return 1
        else:
            return -1


class Resource(object):
    """Resource wrapper.

    Attributes:
        name (str): Name of the resource.
        path (str): Path to the resource file.
        data (object): The resource being wrapped.
        category (list[str]): Different categories this resource is classified
            under.
    """
    def __init__(self, name, path, resource=None, category=''):
        self.name = name
        self.path = path
        self.data = resource

        self.__categories = []
        self.category = category

    @property
    def category(self):
        return self.__categories

    @category.setter
    def category(self, groups):
        self.__categories = groups.split()

    def member_of(self, category):
        """Returns True, if resource is a member of the specified category."""
        return category in self.__categories


class ResourceManager(dict):
    """Resource Management class.

    Inherits from dict, therefore all regular dict operations are usable here.

    Note:
        Can use contains to find a resource by name OR value.
        (contains being: resource in ResourceManager).
    """
    def __init__(self):
        super().__init__()
        # self._resources = dict()

    def __contains__(self, item):
        if isinstance(item, Resource):
            for _, v in self.items():
                if v == item:
                    return True
            return False
        else:
            return super().__contains__(item)

    def add(self, *resources):
        """Add resource(s) to ResourceManager.

        Args:
            *resources (peachy.utils.Resource): An argument list, each argument
                is a Resource.

        Warning:
            Will overwrite any resource that has the same name.
        """
        for resource in resources:
            if resource.name in self:
                logging.warning('Resource overriden %s' % resource.name)
            self[resource.name] = resource
        return self[resource.name]

    def get(self, resource):
        """Get a resource by name or path."""
        # Get by resource name
        if resource in self:
            return super().get(resource)

        # Get by resource path
        else:
            for k, v in self.items():
                if v.path == resource:
                    return self[k]

    def get_category(self, category):
        """Get every resource of a specified category."""
        results = []
        for _, resource in self.items():
            if resource.member_of(category):
                results.append(resource)
        return results

    def remove(self, res):
        """Remove a resource by name, path, or reference."""
        if type(res) == str:
            # Get by resource name
            if res in self:
                return self.pop(res)

            # Get by resource path
            for k, v in self.items():
                if v.path == res:
                    return self.pop(k)
        else:
            # Get by reference
            for k, v in self.items():
                if v == res:
                    return self.pop(k)
        return None

    def remove_category(self, category):
        """Remove an entire category of resources."""
        results = []
        for key, resource in dict_wrap(self):
            if resource.member_of(category):
                results.append(self.pop(key))
        return results

    def rename(self, old_name, new_name):
        """Rename a resource in place."""
        try:
            self[new_name] = self.pop(old_name)
        except KeyError:
            pass
