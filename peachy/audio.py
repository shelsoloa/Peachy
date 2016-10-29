# TODO redo module
import pygame
from pygame.mixer import Sound

# TODO this entire module is a mess and the weakest aspect of Peachy.
# A lot of work can be done here.


class Music(object):

    def __init__(self, source):
        self.source = source
        self.loaded = False
        self.paused = False
        self.playing = False

    def load(self):
        pygame.mixer.music.load(self.source)
        self.loaded = True
        self.paused = False
        self.playing = False

    def pause(self):
        if not self.loaded:
            return
        pygame.mixer.music.pause()
        self.paused = True
        self.playing = False

    def play(self):
        if not self.loaded:
            return
        pygame.mixer.music.play()
        self.paused = False
        self.playing = True

    def resume(self):
        if not self.loaded:
            return
        pygame.mixer.music.unpause()
        self.paused = False
        self.playing = True

    def stop(self):
        if not self.loaded:
            return
        pygame.mixer.music.stop()
        self.paused = False
        self.playing = False


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
