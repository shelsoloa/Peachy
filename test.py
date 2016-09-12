import peachy
from peachy import PC, Engine, World


def main():
    # Create Game
    game = Engine((320, 240), 'Game')

    # Create and configure world
    world = game.add_world(World('Play'))
    world.stage.add(Nub(100, 100))

    # Run game
    game.run()
    

# Example entity
class Nub(peachy.Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 16
        self.height = 16
        
    def render(self):
        peachy.graphics.set_color(255, 255, 0)
        peachy.graphics.draw_entity_rect(self)

    def update(self):
        if peachy.utils.Input.down('left'):
            self.x -= 1
        if peachy.utils.Input.down('right'):
            self.x += 1
        if peachy.utils.Input.down('up'):
            self.y -= 1
        if peachy.utils.Input.down('down'):
            self.y += 1


if __name__ == '__main__':
    main()
