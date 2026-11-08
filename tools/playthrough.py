"""Automated end-to-end playthrough under a virtual display.

Drives the REAL widgets - it finds the Continue button and clicks it, types
into the actual entry box, clicks the actual option rows - so anything a player
could hit, this hits.  For every challenge it deliberately submits a wrong
answer first and checks that a specific diagnosis comes back, then submits the
right one and checks the game advances.

    xvfb-run -a python tools/playthrough.py [--shots]
"""

import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk

from rquest import ui
from rquest.app import App
from rquest.progress import SAVE
from rquest.steps import (Say, Explain, Show, RDemo, AskText, AskChoice, Recap,
                          resolve)

SHOTS = "--shots" in sys.argv
SHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shots")
problems = []
shot_n = [0]


def note(msg):
    problems.append(msg)
    print("   !! " + msg)


def walk(w, want):
    out = []
    for k in w.winfo_children():
        if isinstance(k, want):
            out.append(k)
        out.extend(walk(k, want))
    return out


def pump(app, n=3):
    for _ in range(n):
        app.update_idletasks()
        app.update()


def settle(app, seconds=1.4):
    """Let the staggered card reveal (and any other after() jobs) finish."""
    end = time.time() + seconds
    while time.time() < end:
        app.update_idletasks()
        app.update()
        time.sleep(0.01)


def shot(app, name):
    if not SHOTS:
        return
    os.makedirs(SHOT_DIR, exist_ok=True)
    settle(app, 1.2)
    shot_n[0] += 1
    path = os.path.join(SHOT_DIR, f"{shot_n[0]:02d}-{name}.png")
    os.system(f'import -window root "{path}" 2>/dev/null || '
              f'xwd -root -silent | convert xwd:- "{path}" 2>/dev/null')


def buttons(app):
    return {b.label.cget("text"): b for b in walk(app.actions, ui.Button)}


def click(app, label_starts):
    for text, b in buttons(app).items():
        if text.startswith(label_starts):
            b._on_release()
            pump(app)
            return True
    return False


def close_modal(app):
    pump(app)
    tops = [w for w in app.winfo_children() if isinstance(w, tk.Toplevel)]
    for t in tops:
        shot(app, "recap-modal")
        for b in walk(t, ui.Button):
            b._on_release()
            pump(app)
            return True
    return False


def type_answer(app, text):
    ents = walk(app.content.inner, tk.Entry)
    txts = [t for t in walk(app.content.inner, tk.Text)]
    if ents:
        ents[0].delete(0, "end")
        ents[0].insert(0, text)
        return True
    if txts:
        txts[0].delete("1.0", "end")
        txts[0].insert("1.0", text)
        return True
    return False


def feedback_text(app):
    holder = getattr(app, "fb_holder", None)
    if holder is None:
        return ""
    return " ".join(l.cget("text") for l in walk(holder, tk.Label))


WRONG_TEXT = "mean(x)"
WRONG_NUM = "-999"


def answer_clean(app, step):
    """Answer correctly first time, for the star-rating check."""
    if isinstance(step, AskChoice):
        walk(app.content.inner, ui.OptionButton)[step.correct]._click()
    else:
        fspec = step.free() if callable(step.free) else step.free
        nspec = step.numeric() if callable(step.numeric) else step.numeric
        type_answer(app, fspec["model"] if fspec else
                    f"{nspec[0]:.6f}" if nspec else step.answers[0])
        click(app, "Check")
    pump(app)
    click(app, "Continue")


def play_clean(app, n):
    """A flawless run of one level, to confirm it earns three stars."""
    app.start_level(n)
    pump(app, 3)
    guard = 0
    while app.level is not None and guard < 300:
        guard += 1
        if app.idx >= len(app.level.steps):
            break
        step = app.level.steps[app.idx]
        if isinstance(step, (AskText, AskChoice)):
            answer_clean(app, step)
        elif isinstance(step, Recap):
            if not close_modal(app):
                app._advance()
        else:
            click(app, "Continue")
        pump(app)


def do_asktext(app, step, tag):
    fspec = step.free() if callable(step.free) else step.free
    nspec = step.numeric() if callable(step.numeric) else step.numeric

    # 1) a deliberately wrong answer must produce feedback and NOT advance
    before = app.idx
    wrong = ("this is wrong" if fspec else WRONG_NUM if nspec else WRONG_TEXT)
    type_answer(app, wrong)
    click(app, "Check")
    if app.idx != before:
        note(f"{tag}: a wrong answer advanced the game")
    fb = feedback_text(app)
    if "NOT QUITE" not in fb:
        note(f"{tag}: wrong answer produced no feedback banner")
    elif len(fb) < 60:
        note(f"{tag}: feedback is suspiciously short: {fb[:80]!r}")
    shot(app, f"{tag}-wrong")

    # 2) the hint button, where the step offers one
    if "Hint" in "".join(buttons(app)) or any(t.startswith("Hint") for t in buttons(app)):
        click(app, "Hint")
        if "HINT" not in feedback_text(app):
            note(f"{tag}: Hint button produced no hint")

    # 3) the model answer must be accepted and must advance
    good = (fspec["model"] if fspec else f"{nspec[0]:.6f}" if nspec else step.answers[0])
    type_answer(app, good)
    click(app, "Check")
    fb = feedback_text(app)
    if "CORRECT" not in fb:
        note(f"{tag}: model answer {good!r} was rejected -> {fb[:140]}")
    shot(app, f"{tag}-right")
    if not click(app, "Continue"):
        note(f"{tag}: no Continue button after a correct answer")


def do_askchoice(app, step, tag):
    opts = walk(app.content.inner, ui.OptionButton)
    if len(opts) != len(step.options):
        note(f"{tag}: {len(opts)} option rows drawn for {len(step.options)} options")
        return
    wrong = 0 if step.correct != 0 else 1
    before = app.idx
    opts[wrong]._click()
    pump(app)
    if app.idx != before:
        note(f"{tag}: a wrong option advanced the game")
    if "NOT QUITE" not in feedback_text(app):
        note(f"{tag}: wrong option produced no feedback")
    shot(app, f"{tag}-wrong")
    opts[step.correct]._click()
    pump(app)
    if "CORRECT" not in feedback_text(app):
        note(f"{tag}: correct option was not accepted")
    if not click(app, "Continue"):
        note(f"{tag}: no Continue after the correct option")


def play_level(app, n, start):
    start()
    pump(app, 4)
    guard = 0
    while app.level is not None and guard < 300:
        guard += 1
        if app.idx >= len(app.level.steps):
            break
        step = app.level.steps[app.idx]
        tag = f"L{n}s{app.idx + 1}"
        if isinstance(step, (Say, Explain, Show, RDemo)):
            if app.idx in (1, 3) and n in (1, 5, 10):
                shot(app, f"{tag}-{type(step).__name__.lower()}")
            # a plot step must actually have produced a canvas widget
            if isinstance(step, Show):
                settle(app)
                cv = [w for w in walk(app.content.inner, tk.Widget)
                      if w.winfo_class() == "Canvas" and w.winfo_ismapped()
                      and w.winfo_width() > 300 and w.winfo_height() > 200]
                if not cv:
                    note(f"{tag}: Show step rendered no plot canvas")
                else:
                    px = cv[0].winfo_width() * cv[0].winfo_height()
                    if px < 150000:
                        note(f"{tag}: plot canvas is only "
                             f"{cv[0].winfo_width()}x{cv[0].winfo_height()}")
            if not click(app, "Continue"):
                note(f"{tag}: no Continue button on a {type(step).__name__} step")
                break
        elif isinstance(step, AskText):
            do_asktext(app, step, tag)
        elif isinstance(step, AskChoice):
            do_askchoice(app, step, tag)
        elif isinstance(step, Recap):
            if not close_modal(app):
                note(f"{tag}: recap modal did not appear")
                app._advance()
                pump(app)
        else:
            note(f"{tag}: unknown step type {type(step).__name__}")
            break
    if guard >= 300:
        note(f"L{n}: playthrough did not terminate")


def main():
    if os.path.exists(SAVE):
        os.rename(SAVE, SAVE + ".bak")
    app = App()
    app.geometry("1180x772")
    pump(app, 6)
    shot(app, "home")

    for n in range(1, 11):
        print(f"-- Level {n}")
        xp_before = app.progress.xp
        play_level(app, n, lambda k=n: app.start_level(k))
        pump(app, 4)
        if n not in app.progress.completed:
            note(f"L{n}: did not register as completed")
        if app.progress.xp <= xp_before:
            note(f"L{n}: awarded no XP")
        # this run answers every challenge wrongly once on purpose, so one star
        # is the correct outcome; three stars are checked separately below.
        if app.progress.stars.get(n, 0) != 1:
            note(f"L{n}: a wrong-first run scored "
                 f"{app.progress.stars.get(n, 0)} stars, expected 1")
        shot(app, f"L{n}-complete")
        # the level-complete screen must offer a way onward
        if not (click(app, f"Level {n + 1}") or click(app, "The boss")):
            note(f"L{n}: level-complete screen had no forward button")
        pump(app, 3)
        if n < 10:
            app.show_home()
            pump(app, 2)

    print("-- flawless replay of Level 1 (star check)")
    app.progress.stars[1] = 0
    play_clean(app, 1)
    pump(app, 4)
    if app.progress.stars.get(1, 0) != 3:
        note(f"a flawless run of Level 1 scored {app.progress.stars.get(1,0)} "
             "stars, expected 3")
    app.show_home()
    pump(app, 2)

    print("-- Boss")
    if not app.progress.boss_unlocked():
        note("boss did not unlock after ten levels")
    play_level(app, 11, app.start_boss)
    pump(app, 6)
    if not app.progress.boss_done:
        note("boss did not register as done")
    shot(app, "boss-report")

    app.show_home()
    pump(app, 4)
    shot(app, "home-complete")

    print(f"\nfinal: {app.progress.xp} XP, rank {app.progress.rank()}, "
          f"{len(app.progress.completed)}/10 levels, "
          f"{app.progress.total_stars}/30 stars, "
          f"boss {app.progress.boss_score*100:.0f}%")
    app.destroy()
    if os.path.exists(SAVE):
        os.remove(SAVE)
    if os.path.exists(SAVE + ".bak"):
        os.rename(SAVE + ".bak", SAVE)

    print()
    if problems:
        print(f"{len(problems)} PROBLEM(S):")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("playthrough clean: every level and the boss completed end to end")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(2)
