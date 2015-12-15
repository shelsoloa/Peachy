import peachy
from peachy import pc

class Nub(peachy.Entity):
    def __init__(self, x, y):
        super(self.__class__, self).__init__(x, y)

        self.width = 16
        self.height = 16
        
    def render(self):
        peachy.graphics.set_color(255, 255, 0)
        peachy.graphics.draw_rect(self.x, self.y, self.width, self.height)

    def update(self):
        temp_x = self.x
        temp_y = self.y

        if peachy.inpt.down('LEFT'):
            temp_x -= 1
        if peachy.inpt.down('RIGHT'):
            temp_x += 1
        if peachy.inpt.down('UP'):
            temp_y -= 1
        if peachy.inpt.down('DOWN'):
            temp_y += 1

        self.x = temp_x
        self.y = temp_y

pc.init((320, 240), fps=60, scale=2, debug=True)
pc.entity_room.add(Nub(100, 100))
pc.run()
