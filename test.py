import peachy
from peachy import PC, Engine, World

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

        if peachy.utils.Input.down('left'):
            temp_x -= 1
        if peachy.utils.Input.down('right'):
            temp_x += 1
        if peachy.utils.Input.down('up'):
            temp_y -= 1
        if peachy.utils.Input.down('down'):
            temp_y += 1

        self.x = temp_x
        self.y = temp_y

game = Engine((320, 240), 'Game')
world = game.add_world(World('Play'))
world.entities.add(Nub(100, 100))
game.run()

# PC.init((320, 240), fps=60, scale=2, debug=True)
# PC.engine.world.add(Nub(100, 100))
# PC.run()
