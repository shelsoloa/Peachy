import peachy
import peachy.graphics
import peachy.utils


def _iter_widget(widget):
    for child in widget.children:
        if child.children:
            for c in _iter_widget(child):
                yield c
        else:
            yield child


class UICanvas(object):
    def __init__(self, world):
        self.world = world
        self.widgets = []
        self._focused_widget = None

    @property
    def focused_widget(self):
        return self._focused_widget

    @focused_widget.setter
    def focused_widget(self, widget):
        if self._focused_widget:
            self._focused_widget.focused = False
        if widget:
            widget.focused = True
        self._focused_widget = widget

    """
    A generator that recurses through every widget including child widgets.
    Returns widgets in FIFO order and children in LIFO

    TODO change children to also return FIFO
    """
    def all_widgets(self):
        # Iteration is reversed because widgets are processed FIFO
        for w in range(len(self.widgets) - 1, -1, -1):
            widget = self.widgets[w]
            # Wraps iter_widget to allow for iteration of UICanvas widgets
            for child in _iter_widget(widget):
                yield child
            yield widget

    def get_name(self, name):
        for widget in self.all_widgets():
            if widget.name == name:
                return widget

    def add(self, widget):
        widget.parent = self
        if self.focused_widget is None:
            widget.focused = True
            self.focused_widget = widget
        self.widgets.append(widget)
        return widget

    def remove(self, widget):
        widget.parent = None
        if self.focused_widget == widget:
            self.focused_widget = None
        self.widgets.remove(widget)

    def render(self):
        for widget in self.widgets:
            if widget.visible:
                widget.render()
                widget.render_children()

    def resize(self):
        for widget in self.widgets:
            widget.resize()

    def poll_widgets(self):
        """
        Cycle through widgets and fire Widget.clicked(). Attempt to change focus
        to the last Widget that was clicked.
        Note: Widget.clicked() is only fired for the Widget with the highest
        z-order at Mouse.location
        """
        mx, my = peachy.utils.Mouse.location

        for widget in self.all_widgets():
            if widget.x <= mx <= widget.x + widget.width and \
               widget.y <= my <= widget.y + widget.height and \
               widget.active:
                widget.clicked(mx, my)
                while widget:
                    if widget.focusable:
                        self.focused_widget = widget
                        break
                    else:
                        widget = widget.parent
                break

    def update(self):
        if peachy.utils.Mouse.pressed('left'):
            self.poll_widgets()

        for widget in self.widgets:
            if widget.active:
                widget.update()
                widget.update_children()


class Widget(object):
    def __init__(self, x, y, width=0, height=0, name=''):
        self.name = name

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.active = True
        self.visible = True
        self._focus = False

        self.parent = None
        self.children = []

        self.can_focus = True

    @property
    def focused(self):
        return self._focus

    @focused.setter
    def focused(self, value):
        if self.can_focus:
            self._focus = value
            if value and self.parent is not None:
                self.parent.focused = True
        else:
            raise AttributeError("This Widget cannot be focused.")

    def add(self, widget):
        """ Add a child to this widget """
        widget.parent = self
        self.children.append(widget)
        return widget

    def all_children(self):
        # Iteration is reverse because widgets are processed FIFO
        for w in range(len(self.children) - 1, -1, -1):
            widget = self.children[w]
            for child in _iter_widget(widget):
                yield child
            yield widget

    def clicked(self, x, y):
        return

    def child_clicked(self):
        return

    def move(self, x, y):
        self.x = x
        self.y = y

    def normalize(self, x, y):
        return x - self.x, y - self.y

    def render(self):
        return

    def render_children(self):
        for child in self.children:
            if child.visible:
                child.render()

    def remove(self, widget):
        widget.parent = None
        if self.focused_widget == widget:
            self.focused_widget = self
        self.children.remove(widget)

    def resize(self):
        for widget in self.children:
            widget.resize()

    def update(self):
        return

    def update_children(self):
        for child in self.children:
            if child.active:
                child.update()


class ButtonWidget(Widget):
    """
    The ButtonWidget connects a function to its click event
    Use bind() to connect a function that will be executed by clicked()
    """

    def __init__(self, x, y, width, height,
                 name='', label='',
                 background_color=None, label_color=None):
        super().__init__(x, y, width, height, name)

        self.__actions = []
        self.background_color = background_color
        self.label_color = label_color
        self.label = label

    def clicked(self, x, y):
        for action, args in self.__actions:
            action(*args)

    def bind(self, f, *args):
        self.__actions.append((f, args))

    def render(self):
        try:
            peachy.graphics.set_color(*self.background_color)
            peachy.graphics.draw_entity_rect(self)
        except (AttributeError, TypeError):
            pass

        try:
            peachy.graphics.set_color(*self.label_color)
            peachy.graphics.draw_text(self.label, self.x, self.y)
        except (AttributeError, TypeError):
            pass


class DialogWidget(Widget):
    """
    The DialogWidget can be moved and is always on top
    """

    def __init__(self, x, y, width=0, height=0, name='', label=''):
        super().__init__(x, y, width, height, name)
        self.background_color = (0, 0, 0)
        self.highlight_color = (255, 255, 255)
        self.label = label
        self.previous_mx = None
        self.previous_my = None
        self.dragging = False

    def close(self):
        self.parent.remove(self)
        self.active = False
        self.visible = False

    def render(self):
        peachy.graphics.set_color(*self.background_color)
        peachy.graphics.draw_entity_rect(self)
        peachy.graphics.set_color(*self.highlight_color)
        peachy.graphics.draw_rect(self.x, self.y, self.width, 16)
        peachy.graphics.set_color(*self.background_color)
        peachy.graphics.draw_text(self.label, self.x, self.y)

    def update(self):
        if peachy.utils.Mouse.released('left'):
            self.previous_mx = None
            self.previous_my = None
            self.dragging = False

        elif self.dragging:
            dx = peachy.utils.Mouse.x - self.previous_mx
            dy = peachy.utils.Mouse.y - self.previous_my
            self.x += dx
            self.y += dy
            for child in self.all_children():
                child.x += dx
                child.y += dy
            self.previous_mx = peachy.utils.Mouse.x
            self.previous_my = peachy.utils.Mouse.y

        elif self.focused and peachy.utils.Mouse.pressed('left'):
            mx = peachy.utils.Mouse.x
            my = peachy.utils.Mouse.y
            if self.x <= mx <= self.x + self.width and \
               self.y <= my <= self.y + 16:
                self.previous_mx = mx
                self.previous_my = my
                self.dragging = True


class TextBoxWidget(Widget):

    def __init__(self, x, y, width, height, name=''):
        super().__init__(x, y, width, height, name)
        self.text_capture = peachy.utils.TextCapture()

    def update(self):
        if self.focused:
            self.text_capture.update()

    def render(self):
        peachy.graphics.set_color(255, 255, 255)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)
        peachy.graphics.set_color(0, 0, 0)
        peachy.graphics.draw_text(self.text_capture.value, self.x, self.y)
