"""Extra peachy

A collection of random helpful entities, classes, and functions. Quarantined
to a seperate module to prevent circular dependency and reduce mess.

Basically, anything that doesn't have a home (yet) goes here.
"""

import peachy


class AStarGrid(object):
    """ Has not been updated to conform with current StageData object """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstructions = []

    def in_bounds(self, location):
        x, y = location
        if 0 <= x < self.width and 0 <= y < self.width:
            return True
        return False

    def cost(self, location, destination):
        x1, y1 = location
        x2, y2 = destination

        if (x1 - x2) == 0 or (y1 - y2) == 0:
            return 1
        else:
            return 1.5

    def passable(self, location):
        return location not in self.obstructions

    def neighbours_dep(self, location):
        x, y = location
        results = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results

    def neighbours(self, location):
        x, y = location
        results = []

        for translation in [(0, 1), (0, -1), (1, 0), (1, 1),
                            (1, -1), (-1, 0), (-1, 1), (-1, -1)]:

            trans_x, trans_y = translation
            destination = (x + trans_x, y + trans_y)

            if self.passable(destination):

                if trans_x != 0 and trans_y != 0:
                    border_one = (x + trans_x, y)
                    border_two = (x, y + trans_y)
                    if self.passable(border_one) and self.passable(border_two):
                        results.append(destination)
                else:
                    results.append(destination)

        results = filter(self.in_bounds, results)
        return results


class Camera(peachy.Entity):
    """2D Camera.

    Attributes:
        name (str): The Entity.name for the Camera. Is set to 'peachy-camera'.
        width (int): The width of the view.
        height (int): The height of the view.

        min_x (int): The minimum value of the x-coordinate.
        max_x (int): The maximum value of the x-coordinate.
        min_y (int): The minimum value of the y-coordinate.
        max_y (int): The maximum value of the y-coordinate.

        speed (int): The speed the Camera moves at when panning.
    """

    def __init__(self, view_width, view_height, speed=1):
        super().__init__()
        self.name = 'peachy-camera'
        self.width = view_width
        self.height = view_height
        self.visible = False

        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None

        self.speed = speed

    @staticmethod
    # TODO remove from Camera class and just throw somewhere
    def to_inbounds(num, minimum, maximum):
        """Get the closest int that is also inbounds.

        Args:
            num (int): The number to check for bounding.
            minimum (int): The minimum value of num.
            maximum (int): The maximum value of num.

        Returns:
            int: num if in range, minimum if num is less, or maximum if num is
                more.
        """
        if minimum is not None and num < minimum:
            return minimum
        elif maximum is not None and num > maximum:
            return maximum
        else:
            return num

    def follow(self, entity, center=True):
        """Set the camera to follow a peachy.Entity.

        Args:
            entity (peachy.Entity): The entity to follow.
            center (bool, optional): Whether the camera should center on the
                specified entity. Defaults to True.
        """
        self.following = entity
        self.centering = center

    def pan_to(self, target_x, target_y, center=False):
        """Pan to a specified point.

        Args:
            target_x (int): The x coordinate to pan to.
            target_y (int): The y coordinate to pan to.
            center (boolean)
        """
        self.target_x = target_x
        self.target_y = target_y
        self.centering = True

    def pan_x(self, target, center=False, speed=None):
        if speed is None:
            speed = self.speed

        if center:
            target -= self.width / 2

        target = Camera.to_inbounds(target, self.min_x, self.max_x)

        if self.x + speed < target:
            self.x += speed
        elif self.x - speed > target:
            self.x -= speed
        else:
            self.x = target

    def pan_y(self, target, center=False, speed=None):
        if speed is None:
            speed = self.speed
        if center:
            target -= self.height / 2

        target = Camera.to_inbounds(target, self.min_y, self.max_y)

        if self.y + speed < target:
            self.y += speed
        elif self.y - speed > target:
            self.y -= speed
        else:
            self.y = target

    def snap_to(self, target_x, target_y, center=False):
        self.stop_following()
        self.snap_x(target_x, center)
        self.snap_y(target_y, center)

    def snap_x(self, target, center=False):
        if center:
            target -= self.width / 2

        self.x = Camera.to_inbounds(target, self.min_x, self.max_x)

    def snap_y(self, target, center=False):
        if center:
            target -= self.height / 2
        self.y = Camera.to_inbounds(target, self.min_y, self.max_y)

    def stop_following(self):
        self.following = None
        self.target_x = None
        self.target_y = None

    def update(self):
        if self.following:
            self.target_x = self.following.x
            self.target_y = self.following.y

        if self.target_x:
            self.pan_x(self.target_x, self.centering)
        if self.target_y:
            self.pan_y(self.target_y, self.centering)

    def translate(self):
        peachy.graphics.translate(self.x, self.y)


class TimedEvent(peachy.Entity):
    """A wrapper for peachy.utils.Counter.

    Allows for adding Counter directly to a room. Advances automatically
    each cycle.

    Added to group 'peachy-timed-event'

    Example (assuming initialization within a peachy.Entity function):
        ...
        # Destroy this entity after 10 cycles
        >>> self.container.add(TimerEvent(0, 10, self.destroy, [self]))
        # Destroy this entity after pingpong timer
        >>> counter = Counter(0, 10, enabled_pingpong=True)
        >>> self.container.add(TimedEvent(counter, self.destroy, [self]))

    Attributes:
        counter (peachy.utils.Counter): reference to the nested counter
    """

    def __init__(self, duration, callback=None, callback_args=None):
        """Initialize TimedEvent.

        Args:
            duration (int OR peachy.utils.Counter): The delay on this event.
                Can also pass a peachy.utils.Counter for more advanced
                configuration.

        """
        super().__init__()
        self.group = 'peachy-timed-event'

        if type(duration) is peachy.utils.Counter:
            self.counter = duration
        else:
            self.counter = peachy.utils.Counter(
                0, duration, callback=callback, callback_args=callback_args)

    def update(self):
        if self.counter.advance():
            self.destroy()


class TextCapture(object):
    """
    The TextCapture takes all alphanumeric input recorded by Key and stores it
    inside of self.value

    ex: Name input

    Attributes:
        value (str): the string typed into the TextCapture thus far

    Todo:
        Use Input.last_100 instead of surveying
    """

    def __init__(self, value=''):
        self.value = value

    def update(self):
        keys = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', '_', '-',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            ' '
        ]

        shift = peachy.utils.Key.down('lshift') or \
            peachy.utils.Key.down('rshift')

        if peachy.utils.Key.pressed('backspace') or \
           peachy.utils.Key.pressed('delete'):
            self.value = self.value[:-1]

        for key in keys:
            if peachy.utils.Key.pressed(key):
                if shift:
                    self.value += key.upper()
                else:
                    self.value += key
