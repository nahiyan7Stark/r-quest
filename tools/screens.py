"""Capture the key screens so the interface can be eyeballed without a display."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from rquest import ui
from rquest.app import App
from rquest.progress import SAVE
from rquest.steps import AskText, AskChoice, Recap

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shots")
os.makedirs(OUT, exist_ok=True)
n = [0]


def walk(w, want):
    out = []
    for k in w.winfo_children():
        if isinstance(k, want): out.append(k)
        out.extend(walk(k, want))
    return out


def settle(app, s=1.3):
    end = time.time() + s
    while time.time() < end:
        app.update_idletasks(); app.update(); time.sleep(0.01)


def shot(app, name):
    settle(app)
    n[0] += 1
    os.system(f'import -window root "{OUT}/{n[0]:02d}-{name}.png" 2>/dev/null')
    print("  shot", name)


def click(app, starts):
    for b in walk(app.actions, ui.Button):
        if b.label.cget("text").startswith(starts):
            b._on_release(); app.update(); return True
    return False


def goto(app, lvl, idx):
    app.start_level(lvl); app.idx = idx; app.render_step(); settle(app, 0.9)


if os.path.exists(SAVE): os.rename(SAVE, SAVE + ".bak")
app = App(); app.geometry("1180x780"); settle(app, 1.0)
shot(app, "home-fresh")

# pretend some progress so the map and HUD look lived-in
app.progress.completed = {1, 2, 3}
app.progress.stars = {1: 3, 2: 2, 3: 3}
app.progress.xp = 285
app.show_home(); shot(app, "home-in-progress")

goto(app, 1, 1);  shot(app, "L1-explain")
goto(app, 1, 2);  shot(app, "L1-rdemo-console")
goto(app, 1, 10); shot(app, "L1-plot-barplot")
goto(app, 1, 3)
ents = walk(app.content.inner, tk.Entry)
ents[0].insert(0, "scores <- 12, 7, 19, 4"); click(app, "Check")
shot(app, "L1-challenge-diagnosis")
ents = walk(app.content.inner, tk.Entry)
ents[0].delete(0, "end"); ents[0].insert(0, "scores <- c(12, 7, 19, 4)")
click(app, "Check"); shot(app, "L1-challenge-correct")

goto(app, 4, 2);  shot(app, "L4-normal-curve")
goto(app, 5, 6);  shot(app, "L5-clt-panels")
goto(app, 8, 12); shot(app, "L8-decision-tree")
goto(app, 9, 10); shot(app, "L9-mosaic")
goto(app, 10, 8); shot(app, "L10-regression-bands")
goto(app, 10, 4); shot(app, "L10-lm-summary")

# a multiple-choice challenge mid-answer
goto(app, 7, 1)
while not isinstance(app.level.steps[app.idx], AskChoice):
    app.idx += 1
app.render_step(); settle(app, 0.8)
opts = walk(app.content.inner, ui.OptionButton)
opts[2]._click(); shot(app, "L7-choice-diagnosis")

# recap modal
goto(app, 2, 0)
for i, s in enumerate(app.level.steps):
    if isinstance(s, Recap): app.idx = i; break
app.render_step(); settle(app, 1.0); shot(app, "recap-modal")
for t in [w for w in app.winfo_children() if isinstance(w, tk.Toplevel)]:
    for b in walk(t, ui.Button): b._on_release(); break
settle(app, 1.0); shot(app, "level-complete")

# boss
app.progress.completed = set(range(1, 11))
app.start_boss(); settle(app, 1.0); shot(app, "boss-brief")
app.idx = 5; app.render_step(); settle(app, 1.0); shot(app, "boss-stage")
app.results = [(0,0,False),(1,0,False),(2,1,False),(3,0,False),
               (4,0,False),(5,2,False),(6,0,False)]
from rquest.levels.boss import _finish
app.level = None; _finish(app); shot(app, "boss-report")

app.destroy()
if os.path.exists(SAVE): os.remove(SAVE)
if os.path.exists(SAVE + ".bak"): os.rename(SAVE + ".bak", SAVE)
print("done")
