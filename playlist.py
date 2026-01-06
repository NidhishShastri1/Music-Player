import os
import random

class Playlist:
    def __init__(self, folder):
        self.songs = []
        self.index = 0
        self.shuffle = False
        self.repeat = False
        self.load(folder)

    def load(self, folder):
        for file in os.listdir(folder):
            if file.endswith((".mp3", ".wav")):
                self.songs.append(os.path.join(folder, file))

    def current(self):
        return self.songs[self.index] if self.songs else None

    def next(self):
        if self.repeat:
            return self.current()

        if self.shuffle:
            self.index = random.randint(0, len(self.songs) - 1)
        else:
            self.index = (self.index + 1) % len(self.songs)
        return self.current()

    def prev(self):
        self.index = (self.index - 1) % len(self.songs)
        return self.current()
