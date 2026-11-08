"""Stars, XP and which levels are unlocked.

Deliberately simple: the scoring exists to give the player a sense of
forward motion, not to grade them.  Nothing here can ever block progress --
a level is unlocked as soon as the one before it has been finished, and
finishing only requires getting to the end, however many retries it took.
"""

from __future__ import annotations

import json
import os

SAVE = os.path.join(os.path.expanduser("~"), ".rquest_progress.json")
N_LEVELS = 10

# XP awarded per challenge by how many tries it took.  Still positive on the
# fourth attempt: persistence is the behaviour we want to reward.
XP_BY_ATTEMPT = [10, 7, 5, 3]


class Progress:
    def __init__(self):
        self.xp = 0
        self.completed = set()          # level numbers finished
        self.stars = {}                 # level -> 0..3
        self.boss_done = False
        self.boss_score = 0.0
        self.load()

    # --- scoring ----------------------------------------------------------
    def award(self, attempt: int) -> int:
        gained = XP_BY_ATTEMPT[min(attempt, len(XP_BY_ATTEMPT) - 1)]
        self.xp += gained
        return gained

    def finish_level(self, n: int, first_try: int, total: int):
        """Stars reflect how many challenges were nailed on the first try."""
        self.completed.add(n)
        if total <= 0:
            s = 3
        else:
            frac = first_try / total
            s = 3 if frac >= 0.85 else 2 if frac >= 0.5 else 1
        self.stars[n] = max(self.stars.get(n, 0), s)
        self.xp += 25
        self.save()

    def unlocked(self, n: int) -> bool:
        return n == 1 or (n - 1) in self.completed

    def boss_unlocked(self) -> bool:
        return len(self.completed) >= N_LEVELS

    @property
    def total_stars(self):
        return sum(self.stars.values())

    def rank(self) -> str:
        for need, name in ((900, "Statistician"), (600, "Analyst"), (350, "Apprentice"),
                           (150, "Data Cadet"), (0, "Newcomer")):
            if self.xp >= need:
                return name
        return "Newcomer"

    # --- persistence ------------------------------------------------------
    def save(self):
        try:
            with open(SAVE, "w") as f:
                json.dump({"xp": self.xp, "completed": sorted(self.completed),
                           "stars": {str(k): v for k, v in self.stars.items()},
                           "boss_done": self.boss_done,
                           "boss_score": self.boss_score}, f)
        except OSError:
            pass        # a read-only home directory must never break play

    def load(self):
        try:
            with open(SAVE) as f:
                d = json.load(f)
            self.xp = int(d.get("xp", 0))
            self.completed = set(int(x) for x in d.get("completed", []))
            self.stars = {int(k): int(v) for k, v in d.get("stars", {}).items()}
            self.boss_done = bool(d.get("boss_done", False))
            self.boss_score = float(d.get("boss_score", 0.0))
        except Exception:
            pass

    def reset(self):
        self.xp = 0
        self.completed = set()
        self.stars = {}
        self.boss_done = False
        self.boss_score = 0.0
        self.save()
