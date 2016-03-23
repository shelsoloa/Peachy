from pygame.mixer import Channel, Sound

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

""" 
 # Deprected pending removal. Replaced by SoundHandler

class SoundEffect(object):

    def __init__(self, sound):
        self.sound = sound
        self.channel = None

    def play(self):
        if self.channel:
            if self.channel.get_sound() == self.sound:
                self.channel.stop()
        self.channel = self.sound.play()

    def playing(self):
        if self.channel:
            if self.channel.get_sound() == self.sound:
                return self.channel.get_busy()
        else:
            return False

    def stop(self):
        if self.channel:
            if self.channel.get_sound() == self.sound:
                self.channel.stop()
                self.channel = None
"""
