import tkinter as tk
import os
import time
import pygame
import random

from playlist import Playlist
from player import MusicPlayer

MUSIC_FOLDER = "music"

# Themes
DARK_THEME = {
    "PRIMARY_BG": "#121212",
    "CARD_BG": "#181818",
    "TEXT_COLOR": "#FFFFFF",
    "SUBTEXT_COLOR": "#B3B3B3",
    "ACCENT": "#1DB954",
    "HIGHLIGHT": "#1ed760"
}

LIGHT_THEME = {
    "PRIMARY_BG": "#f5f5f5",
    "CARD_BG": "#ffffff",
    "TEXT_COLOR": "#000000",
    "SUBTEXT_COLOR": "#555555",
    "ACCENT": "#1DB954",
    "HIGHLIGHT": "#1ed760"
}


class ModernSlider(tk.Canvas):
    def __init__(self, parent, width=400, height=8, command=None, accent="#1DB954"):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.width = width
        self.height = height
        self.value = 0
        self.accent = accent

        self.track = self.create_rectangle(
            0, height // 2 - 3, width, height // 2 + 3,
            fill="#333333", outline=""
        )
        self.fill = self.create_rectangle(
            0, height // 2 - 3, 0, height // 2 + 3,
            fill=self.accent, outline=""
        )
        self.knob = self.create_oval(
            -5, height // 2 - 7, 9, height // 2 + 7,
            fill=self.accent, outline=""
        )

        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)

    def set(self, percent):
        percent = max(0, min(100, percent))
        self.value = percent
        x = (percent / 100) * self.width
        self.coords(self.fill, 0, self.height // 2 - 3, x, self.height // 2 + 3)
        self.coords(self.knob, x - 5, self.height // 2 - 7, x + 9, self.height // 2 + 7)

    def click(self, e):
        self.set((e.x / self.width) * 100)
        if self.command:
            self.command(self.value)

    def drag(self, e):
        self.click(e)


class App:
    def __init__(self, root):
        self.root = root
        self.theme = DARK_THEME
        self.root.title("🎧 Spotify Style Music Player")
        self.root.geometry("750x700")
        self.root.configure(bg=self.theme["PRIMARY_BG"])

        self.playlist = Playlist(MUSIC_FOLDER)
        self.player = MusicPlayer()

        self.shuffle_mode = False
        self.repeat_mode = False
        self.queue = []  # upcoming songs
        self.sleep_timer = None

        self.build_ui()
        self.update_progress()

        # Keyboard shortcuts
        self.root.bind("<space>", lambda e: self.pause())
        self.root.bind("<Right>", lambda e: self.next())
        self.root.bind("<Left>", lambda e: self.prev())

    def build_ui(self):
        self.card = tk.Frame(self.root, bg=self.theme["CARD_BG"], bd=0)
        self.card.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # Theme toggle
        tk.Button(self.card, text="🌗 Theme", command=self.toggle_theme,
                  bg=self.theme["ACCENT"], fg=self.theme["TEXT_COLOR"],
                  bd=0, font=("Segoe UI", 10, "bold")).pack(anchor="ne")

        self.song_label = tk.Label(self.card, text="No song playing",
                                   bg=self.theme["CARD_BG"], fg=self.theme["TEXT_COLOR"],
                                   font=("Segoe UI", 18, "bold"))
        self.song_label.pack(pady=(0, 5))

        self.status_label = tk.Label(self.card, text="Ready",
                                     bg=self.theme["CARD_BG"], fg=self.theme["SUBTEXT_COLOR"],
                                     font=("Segoe UI", 11))
        self.status_label.pack(pady=(0, 15))

        # Playlist
        self.listbox = tk.Listbox(self.card, font=("Segoe UI", 12),
                                  bg="#202020", fg=self.theme["TEXT_COLOR"],
                                  relief="flat", height=10,
                                  selectbackground=self.theme["ACCENT"],
                                  selectforeground=self.theme["TEXT_COLOR"],
                                  activestyle="none")
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=10)
        for s in self.playlist.songs:
            self.listbox.insert(tk.END, os.path.basename(s))

        # Progress bar + time labels
        progress_frame = tk.Frame(self.card, bg=self.theme["CARD_BG"])
        progress_frame.pack(pady=(15, 10))
        self.elapsed_label = tk.Label(progress_frame, text="0:00",
                                      bg=self.theme["CARD_BG"], fg=self.theme["SUBTEXT_COLOR"])
        self.elapsed_label.pack(side=tk.LEFT)
        self.progress = ModernSlider(progress_frame, width=500, accent=self.theme["ACCENT"],
                                     command=self.seek)
        self.progress.pack(side=tk.LEFT, padx=10)
        self.duration_label = tk.Label(progress_frame, text="0:00",
                                       bg=self.theme["CARD_BG"], fg=self.theme["SUBTEXT_COLOR"])
        self.duration_label.pack(side=tk.LEFT)

        # Volume
        vol_frame = tk.Frame(self.card, bg=self.theme["CARD_BG"])
        vol_frame.pack(pady=(0, 20))
        self.volume_icon = tk.Label(vol_frame, text="🔊", bg=self.theme["CARD_BG"],
                                    fg=self.theme["TEXT_COLOR"])
        self.volume_icon.pack(side=tk.LEFT)
        self.volume = ModernSlider(vol_frame, width=200, accent=self.theme["ACCENT"],
                                   command=lambda v: self.player.set_volume(v / 100))
        self.volume.set(70)
        self.volume.pack(side=tk.LEFT, padx=10)

        # Controls
        controls = tk.Frame(self.card, bg=self.theme["CARD_BG"])
        controls.pack(pady=10)
        buttons = [
            ("⏮", self.prev),
            ("▶", self.play),
            ("⏸", self.pause),
            ("⏭", self.next),
            ("🔁", self.toggle_repeat),
            ("🔀", self.toggle_shuffle),
            ("🕒", self.set_sleep_timer),
        ]
        for col, (txt, cmd) in enumerate(buttons):
            btn = tk.Button(controls, text=txt, command=cmd,
                            bg=self.theme["ACCENT"], fg=self.theme["TEXT_COLOR"], bd=0,
                            font=("Segoe UI", 14, "bold"), width=4, height=2)
            btn.grid(row=0, column=col, padx=8, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.theme["HIGHLIGHT"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.theme["ACCENT"]))

        # Queue display
        self.queue_label = tk.Label(self.card, text="Queue: Empty",
                                    bg=self.theme["CARD_BG"], fg=self.theme["SUBTEXT_COLOR"],
                                    font=("Segoe UI", 11))
        self.queue_label.pack(pady=(10, 0))

    # Theme toggle
    def toggle_theme(self):
        self.theme = LIGHT_THEME if self.theme == DARK_THEME else DARK_THEME
        self.root.configure(bg=self.theme["PRIMARY_BG"])
        for widget in self.root.winfo_children():
            widget.destroy()
        self.build_ui()

    # Player controls
    def play(self):
        sel = self.listbox.curselection()
        if sel:
            self.playlist.index = sel[0]
        song = self.playlist.current()
        self.player.load(song)
        self.player.play()
        self.song_label.config(text=os.path.basename(song))
        self.status_label.config(text="Playing")
        self.duration_label.config(text=self.format_time(self.player.duration))

    def pause(self):
        if self.player.paused:
            self.player.resume()
            self.status_label.config(text="Playing")
        else:
            self.player.pause()
            self.status_label.config(text="Paused")

    def next(self):
        if self.queue:  # play from queue first
            song = self.queue.pop(0)
        elif self.shuffle_mode:
            self.playlist.index = random.randint(0, len(self.playlist.songs) - 1)
            song = self.playlist.current()
        elif self.repeat_mode:
            song = self.playlist.current()
        else:
            self.playlist.index = (self.playlist.index + 1) % len(self.playlist.songs)
            song = self.playlist.current()

        self.player.load(song)
        self.player.play()
        self.song_label.config(text=os.path.basename(song))
        self.status_label.config(text="Playing")
        self.duration_label.config(text=self.format_time(self.player.duration))
        self.update_queue_label()

    def prev(self):
        self.playlist.index = (self.playlist.index - 1) % len(self.playlist.songs)
        song = self.playlist.current()
        self.player.load(song)
        self.player.play()
        self.song_label.config(text=os.path.basename(song))
        self.status_label.config(text="Playing")
        self.duration_label.config(text=self.format_time(self.player.duration))

    # ---------------- Repeat & Shuffle ----------------
    def toggle_repeat(self):
        self.repeat_mode = not self.repeat_mode
        self.status_label.config(text="Repeat On" if self.repeat_mode else "Repeat Off")

    def toggle_shuffle(self):
        self.shuffle_mode = not self.shuffle_mode
        self.status_label.config(text="Shuffle On" if self.shuffle_mode else "Shuffle Off")

    # ---------------- Queue ----------------
    def add_to_queue(self):
        sel = self.listbox.curselection()
        if sel:
            song = self.playlist.songs[sel[0]]
            self.queue.append(song)
            self.update_queue_label()

    def update_queue_label(self):
        if self.queue:
            names = [os.path.basename(s) for s in self.queue]
            self.queue_label.config(text="Queue: " + " → ".join(names))
        else:
            self.queue_label.config(text="Queue: Empty")

    # ---------------- Sleep Timer ----------------
    def set_sleep_timer(self):
        # Example: stop after 5 minutes
        self.sleep_timer = time.time() + 5 * 60
        self.status_label.config(text="Sleep Timer: 5 min")

    def check_sleep_timer(self):
        if self.sleep_timer and time.time() >= self.sleep_timer:
            pygame.mixer.music.stop()
            self.status_label.config(text="Stopped (Timer)")
            self.sleep_timer = None

    # ---------------- Progress & Seek ----------------
    def update_progress(self):
        if not self.player.paused and pygame.mixer.music.get_busy():
            elapsed = time.time() - self.player.start_time
            percent = min((elapsed / self.player.duration) * 100, 100)
            self.progress.set(percent)
            self.elapsed_label.config(text=self.format_time(elapsed))
            self.duration_label.config(text=self.format_time(self.player.duration))
        self.check_sleep_timer()
        self.root.after(500, self.update_progress)

    def seek(self, percent):
        if self.player.duration > 0:
            new_time = (percent / 100) * self.player.duration
            pygame.mixer.music.play(start=new_time)
            self.player.start_time = time.time() - new_time

    # ---------------- Helpers ----------------
    def format_time(self, seconds):
        if seconds is None:
            return "0:00"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"


# ---------------- MAIN ----------------
if __name__ == "__main__":
    pygame.init()
    root = tk.Tk()
    App(root)
    root.mainloop()