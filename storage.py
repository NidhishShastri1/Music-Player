import json

FILE = "playlist.json"

def save_playlist(songs):
    with open(FILE, "w") as f:
        json.dump(songs, f)

def load_playlist():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []
