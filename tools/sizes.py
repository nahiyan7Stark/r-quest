"""Check the layout holds together at the window sizes real laptops have."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from rquest.app import App
from rquest.progress import SAVE
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shots-sizes")
os.makedirs(OUT, exist_ok=True)


def settle(app, s=1.2):
    end = time.time() + s
    while time.time() < end:
        app.update_idletasks(); app.update(); time.sleep(0.01)


if os.path.exists(SAVE): os.rename(SAVE, SAVE + ".bak")
app = App()
for w, h, name in [(1024, 700, "1024x700"), (1366, 768, "1366x768"),
                   (960, 660, "960x660-minimum")]:
    app.geometry(f"{w}x{h}")
    settle(app, 0.7)
    app.start_level(10); app.idx = 8; app.render_step()   # the widest plot
    settle(app, 1.3)
    os.system(f'import -window root "{OUT}/{name}-plot.png" 2>/dev/null')
    app.idx = 4; app.render_step()                        # the widest console
    settle(app, 1.1)
    os.system(f'import -window root "{OUT}/{name}-console.png" 2>/dev/null')
    print("  ", name)
app.destroy()
if os.path.exists(SAVE): os.remove(SAVE)
if os.path.exists(SAVE + ".bak"): os.rename(SAVE + ".bak", SAVE)
