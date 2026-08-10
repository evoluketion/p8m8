import json
import os

DEFAULTS = {
    "show_tab_spaces": False,
    "wrap_text": True
}

PREFS_PATH = "prefs.json"


class Prefs:
    def __init__(self):
        self.prefs = self.load_prefs()

    def get(self, key, default=None):
        return self.prefs.get(key, default)

    def set(self, key, value):
        self.prefs[key] = value
        self.save_prefs()

    def load_prefs(self):
        if not os.path.exists(PREFS_PATH):
            self.prefs = dict(DEFAULTS)
            self.save_prefs()
            return dict(DEFAULTS)
        with open(PREFS_PATH, "r") as f:
            data = json.load(f)
        return {**DEFAULTS, **data}

    def save_prefs(self):
        with open(PREFS_PATH, "w") as f:
            json.dump(self.prefs, f, indent=2)