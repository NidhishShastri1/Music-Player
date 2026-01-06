import pygame
import time
from mutagen.mp3 import MP3

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.paused = False
        self.start_time = 0
        self.duration = 0

    def load(self, song):
        pygame.mixer.music.load(song)
        self.duration = int(MP3(song).info.length)

    def play(self):
        pygame.mixer.music.play()
        self.start_time = time.time()
        self.paused = False

    def pause(self):
        pygame.mixer.music.pause()
        self.paused = True

    def resume(self):
        pygame.mixer.music.unpause()
        self.paused = False

    def stop(self):
        pygame.mixer.music.stop()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)
