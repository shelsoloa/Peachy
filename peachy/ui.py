import peachy

class UICanvas(object):
    def __init__(self):
        self.widgets = []
        self.focused_widget = None

    def add(self, widget):
        widget.parent = self
        if self.focused_widget == None:
            self.focused_widget = widget
        self.widgets.append(widget)

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
        # TODO child widgets can not be clicked
        for i in range(len(self.widgets)-1, -1, -1):
            widget = self.widgets[i]
            mx, my = peachy.utils.Mouse.x, peachy.utils.Mouse.y
            wx, wy = widget.get_absolute()
            if wx <= mx <= wx + widget.width and \
               wy <= my <= wy + widget.height:
                widget.clicked()
                if widget.focusable:
                    if self.focused_widget:
                        self.focused_widget.focused = False
                    self.focused_widget = widget
                break

    def update(self):
        if peachy.utils.Mouse.pressed('left'):
            self.poll_widgets()

        for widget in self.widgets:
            if widget.active:
                widget.update()
                widget.update_children()


class Widget(object):
    def __init__(self, x, y, width=0, height=0, label=''):
        self.label = ''

        self.x = x
        self.y = y
        self.width = 0
        self.height = 0

        self.active = True
        self.visible = True
        self._focus = False

        self.parent = None
        self.children = []

        self.focusable = True

    @property
    def focused(self):
        return self._focus

    @focused.setter
    def focused(self, value):
        if self.focusable:
            self._focus = value
            if value == True and self.parent != None:
                self.parent.focused = True
        else:
            raise AttributeError("This Widget cannot be focused.")

    def add(self, widget):
        """ Add a child to this widget """
        widget.parent = self
        self.children.append(widget)

    def clicked(self):
        return

    def get_absolute(self):
        """
        Returns the absolute coordinates of this widget, regardless of its
        nesting.
        """
        # TODO code this to recurse over parents
        # if self.parent == None:
        #     return (self.x, self.y)
        # else:
        #     px, py = self.parent.get_absolute()
        #     return (self.x + px, self.y + py)
        return (self.x, self.y)

    def render(self):
        return

    def render_children(self):
        for child in self.children:
            child.render()

    def resize(self):
        for widget in self.children:
            widget.resize()

    def update(self):
        return

    def update_children(self):
        for child in self.children:
            child.update()
