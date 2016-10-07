# TODO redo module
from pygame.mixer import Sound


class SoundHandler(Sound):
    """ Wrapper for Pygame.Sound that tracks the state of a single sound """

    def __init__(self, sound):
        self.sound = sound
        self.is_playing = False

    def play(self, loops=0, maxtime=0, fade_ms=0):
        if not self.is_playing:
            self.sound.play(loops, maxtime, fade_ms)
            self.is_playing = True

    def stop(self):
        if self.is_playing:
            self.sound.stop()
            self.is_playing = False
