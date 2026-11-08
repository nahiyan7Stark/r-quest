"""Reusable widgets: the visual vocabulary of the game.

Every screen in R Quest is built from these pieces, so the game looks like one
coherent thing rather than ten different forms.  Tk gives us no rounded
corners or CSS, so "polish" here means consistent spacing, a small set of card
types with coloured accent strips, hover states on every button, and a few
cheap animations (typewriter dialogue, counting XP, staggered card reveals)
that make the interface feel alive without costing reliability.
"""

from __future__ import annotations

import tkinter as tk
from . import theme as T


# ==========================================================================
# small helpers
# ==========================================================================

def _lerp_hex(c1, c2, t):
    a = tuple(int(c1[i:i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(c2[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class WrapRegistry:
    """Labels that must re-wrap when the window is resized."""

    def __init__(self):
        self.items = []          # (label, padding)

    def add(self, label, pad=0):
        self.items.append((label, pad))
        return label

    def apply(self, width):
        for lbl, pad in self.items:
            try:
                lbl.configure(wraplength=max(220, width - pad))
            except tk.TclError:
                pass


# ==========================================================================
# buttons
# ==========================================================================

class Button(tk.Frame):
    """A flat button with a real hover and pressed state.

    tk.Button on Windows draws a 3-D chrome widget that would break the look,
    so this is a Label in a Frame with bindings.
    """

    def __init__(self, parent, text, command, kind="primary", width=None,
                 font=None, pad=(18, 9)):
        colours = {
            "primary":  (T.ACCENT_DK, "#4a85e8", "#ffffff"),
            "ghost":    (T.PANEL_ALT, "#2f3a53", T.INK),
            "good":     ("#2f7d55", "#3a9668", "#ffffff"),
            "danger":   ("#8d3b41", "#a8474e", "#ffffff"),
            "quiet":    (T.PANEL, T.PANEL_ALT, T.INK_DIM),
        }
        self.base, self.hover, fg = colours.get(kind, colours["primary"])
        super().__init__(parent, bg=self.base, highlightthickness=0, bd=0)
        self.command = command
        self.enabled = True
        self.label = tk.Label(self, text=text, bg=self.base, fg=fg,
                              font=font or T.F_H2, padx=pad[0], pady=pad[1],
                              cursor="hand2")
        if width:
            self.label.configure(width=width)
        self.label.pack(fill="both", expand=True)
        for w in (self, self.label):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_press)
            w.bind("<ButtonRelease-1>", self._on_release)

    def _paint(self, c):
        self.configure(bg=c)
        self.label.configure(bg=c)

    def _on_enter(self, _=None):
        if self.enabled:
            self._paint(self.hover)

    def _on_leave(self, _=None):
        if self.enabled:
            self._paint(self.base)

    def _on_press(self, _=None):
        if self.enabled:
            self._paint(_lerp_hex(self.base, "#000000", 0.25))

    def _on_release(self, _=None):
        if not self.enabled:
            return
        self._paint(self.hover)
        if self.command:
            self.command()

    def set_enabled(self, on: bool):
        self.enabled = on
        self._paint(self.base if on else T.PANEL_ALT)
        self.label.configure(fg=T.INK if on else T.INK_DIM,
                             cursor="hand2" if on else "arrow")

    def set_text(self, t):
        self.label.configure(text=t)


class OptionButton(tk.Frame):
    """A multiple-choice option: letter badge + wrapping text, whole row clickable."""

    def __init__(self, parent, letter, text, command, wrapreg=None):
        super().__init__(parent, bg=T.PANEL_ALT, highlightthickness=1,
                         highlightbackground=T.BORDER, bd=0)
        self.command = command
        self.enabled = True
        self.badge = tk.Label(self, text=letter, bg=T.ACCENT_DK, fg="#ffffff",
                              font=T.F_H2, width=3, pady=8, cursor="hand2")
        self.badge.pack(side="left", fill="y")
        self.text = tk.Label(self, text=text, bg=T.PANEL_ALT, fg=T.INK,
                             font=T.F_BODY, justify="left", anchor="w",
                             padx=14, pady=10, cursor="hand2", wraplength=620)
        self.text.pack(side="left", fill="both", expand=True)
        if wrapreg:
            wrapreg.add(self.text, 140)
        for w in (self, self.badge, self.text):
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)
            w.bind("<Button-1>", self._click)

    def _enter(self, _=None):
        if self.enabled:
            self.configure(highlightbackground=T.ACCENT)
            self.text.configure(bg="#2b3448")
            self.configure(bg="#2b3448")

    def _leave(self, _=None):
        if self.enabled:
            self.configure(highlightbackground=T.BORDER, bg=T.PANEL_ALT)
            self.text.configure(bg=T.PANEL_ALT)

    def _click(self, _=None):
        if self.enabled and self.command:
            self.command()

    def mark(self, state):
        """state: 'right' | 'wrong' | 'off'"""
        self.enabled = False
        col = {"right": T.GOOD, "wrong": T.BAD, "off": T.BORDER}[state]
        self.configure(highlightbackground=col)
        self.badge.configure(bg=col if state != "off" else T.PANEL,
                             fg="#0d1017" if state != "off" else T.INK_DIM)
        self.text.configure(cursor="arrow")
        self.badge.configure(cursor="arrow")


# ==========================================================================
# scrolling content area
# ==========================================================================

class ScrollArea(tk.Frame):
    def __init__(self, parent, bg=T.BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.vbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                 width=12, troughcolor=T.BG, bg=T.BORDER,
                                 activebackground=T.ACCENT_DK, bd=0,
                                 highlightthickness=0, relief="flat")
        self.canvas.configure(yscrollcommand=self._on_scroll)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vbar.pack(side="right", fill="y")
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._resize_inner)
        self.canvas.bind("<Configure>", self._resize_canvas)
        self.on_width = None
        self._bind_wheel()

    def _on_scroll(self, lo, hi):
        # hide the scrollbar entirely when everything fits: less clutter
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.vbar.pack_forget()
        else:
            self.vbar.pack(side="right", fill="y")
        self.vbar.set(lo, hi)

    def _resize_inner(self, _=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_canvas(self, e):
        self.canvas.itemconfigure(self._win, width=e.width)
        if self.on_width:
            self.on_width(e.width)

    def _bind_wheel(self):
        def wheel(e):
            if self.vbar.winfo_ismapped():
                delta = -1 * (e.delta // 120) if e.delta else (1 if e.num == 5 else -1)
                self.canvas.yview_scroll(delta, "units")
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.bind_all(seq, wheel, add="+")

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self.canvas.yview_moveto(0)

    def to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)


# ==========================================================================
# cards
# ==========================================================================

def card(parent, accent=T.ACCENT, bg=T.PANEL, pady=(0, 14)):
    """A content block with a coloured strip down its left edge."""
    outer = tk.Frame(parent, bg=T.BORDER, highlightthickness=0)
    outer.pack(fill="x", pady=pady, padx=2)
    strip = tk.Frame(outer, bg=accent, width=4)
    strip.pack(side="left", fill="y")
    body = tk.Frame(outer, bg=bg, padx=18, pady=15)
    body.pack(side="left", fill="both", expand=True)
    return body


def card_title(parent, text, colour=T.ACCENT, kicker=None):
    if kicker:
        tk.Label(parent, text=kicker.upper(), bg=parent["bg"], fg=T.INK_DIM,
                 font=(T.F_SMALL[0], 9, "bold"), anchor="w").pack(fill="x")
    tk.Label(parent, text=text, bg=parent["bg"], fg=colour, font=T.F_H1,
             anchor="w", justify="left").pack(fill="x", pady=(2, 8))


def body_text(parent, text, wrapreg=None, fg=T.INK, font=None, pad=(0, 0)):
    lbl = tk.Label(parent, text=text, bg=parent["bg"], fg=fg, font=font or T.F_BODY,
                   justify="left", anchor="w", wraplength=640)
    lbl.pack(fill="x", pady=pad)
    if wrapreg:
        wrapreg.add(lbl, 150)
    return lbl


def glossary(parent, terms, wrapreg=None):
    """The plain-language translation strip: 'technical word = what it means'."""
    if not terms:
        return
    box = tk.Frame(parent, bg=T.PANEL_ALT, padx=12, pady=9)
    box.pack(fill="x", pady=(10, 0))
    tk.Label(box, text="PLAIN ENGLISH", bg=T.PANEL_ALT, fg=T.WARN,
             font=(T.F_SMALL[0], 9, "bold"), anchor="w").pack(fill="x", pady=(0, 5))
    for term, meaning in terms.items():
        row = tk.Frame(box, bg=T.PANEL_ALT)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"{term}", bg=T.PANEL_ALT, fg=T.ACCENT,
                 font=(T.F_CODE[0], 11, "bold"), anchor="nw").pack(side="left")
        lbl = tk.Label(row, text=f"  {meaning}", bg=T.PANEL_ALT, fg=T.INK_DIM,
                       font=T.F_SMALL, justify="left", anchor="w", wraplength=520)
        lbl.pack(side="left", fill="x", expand=True)
        if wrapreg:
            wrapreg.add(lbl, 300)


def console(parent, code=None, output=None, title="R console",
            code_label="> ", height_hint=None):
    """A fake RStudio console pane: traffic lights, the R command, its output."""
    shell = tk.Frame(parent, bg=T.CODE_BG, highlightthickness=1,
                     highlightbackground=T.BORDER)
    shell.pack(fill="x", pady=(8, 4))
    bar = tk.Frame(shell, bg="#161b25")
    bar.pack(fill="x")
    dots = tk.Frame(bar, bg="#161b25")
    dots.pack(side="left", padx=9, pady=6)
    for c in ("#e8737b", "#e8b463", "#59c98a"):
        tk.Canvas(dots, width=9, height=9, bg="#161b25", highlightthickness=0).pack(side="left", padx=2)
        dots.winfo_children()[-1].create_oval(1, 1, 8, 8, fill=c, outline="")
    tk.Label(bar, text=title, bg="#161b25", fg=T.INK_DIM,
             font=(T.F_SMALL[0], 9)).pack(side="left", padx=4)
    inner = tk.Frame(shell, bg=T.CODE_BG, padx=14, pady=11)
    inner.pack(fill="both", expand=True)
    if code:
        for line in str(code).split("\n"):
            row = tk.Frame(inner, bg=T.CODE_BG)
            row.pack(fill="x", anchor="w")
            tk.Label(row, text=code_label, bg=T.CODE_BG, fg=T.ACCENT,
                     font=T.F_CODE).pack(side="left", anchor="n")
            tk.Label(row, text=line, bg=T.CODE_BG, fg=T.CODE_INK, font=T.F_CODE,
                     justify="left", anchor="w").pack(side="left", anchor="n")
    if output:
        # R output is preformatted, so it must never be soft-wrapped -- but a
        # stray long prose line would run off the panel, so wrap only those.
        import textwrap
        lines = []
        for line in str(output).rstrip("\n").split("\n"):
            if len(line) > 92 and " " in line.strip():
                lines.extend(textwrap.wrap(line, 88) or [""])
            else:
                lines.append(line)
        tk.Label(inner, text="\n".join(lines), bg=T.CODE_BG, fg="#cbd6ea",
                 font=T.F_CODE_S, justify="left", anchor="w").pack(
            fill="x", anchor="w", pady=(6 if code else 0, 0))
    return shell


def feedback(parent, ok, text, wrapreg=None):
    col = T.GOOD if ok else T.WARN
    box = tk.Frame(parent, bg=T.PANEL_ALT, highlightthickness=1, highlightbackground=col)
    box.pack(fill="x", pady=(10, 2))
    head = tk.Frame(box, bg=col)
    head.pack(fill="x")
    tk.Label(head, text=("  CORRECT" if ok else "  NOT QUITE - HERE IS WHAT HAPPENED"),
             bg=col, fg="#0d1017", font=(T.F_SMALL[0], 9, "bold"), anchor="w",
             pady=3).pack(fill="x")
    lbl = tk.Label(box, text=text, bg=T.PANEL_ALT, fg=T.INK, font=T.F_BODY,
                   justify="left", anchor="w", wraplength=620, padx=13, pady=11)
    lbl.pack(fill="x")
    if wrapreg:
        wrapreg.add(lbl, 170)
    return box


# ==========================================================================
# Professor Byte
# ==========================================================================

MOODS = ("talk", "happy", "think", "cheer")


def draw_byte(cv: tk.Canvas, mood="talk", size=78, bg=T.PANEL):
    """Draw the NPC on a canvas.  Vector shapes only -- no image files, so the
    game folder stays small and there is nothing to fail to load."""
    cv.delete("all")
    cv.configure(bg=bg)
    s = size / 100.0
    # the drawing runs from y = 0 (tassel) to y = 122 (shoulders); centre that
    # inside whatever canvas we were given so nothing is clipped either end.
    ox = max(0.0, (int(cv["width"]) - 100 * s) / 2)
    oy = max(0.0, (int(cv["height"]) - 122 * s) / 2)

    def sc(*p):
        return [(p[i] * s + (ox if i % 2 == 0 else oy)) for i in range(len(p))]

    body = T.ACCENT if mood != "cheer" else "#8fc0ff"
    # shoulders
    cv.create_oval(*sc(14, 74, 86, 122), fill="#2b4a80", outline="")
    # head
    cv.create_rectangle(*sc(18, 26, 82, 80), fill=body, outline="", width=0)
    cv.create_oval(*sc(18, 18, 82, 46), fill=body, outline="")
    cv.create_oval(*sc(18, 62, 82, 92), fill=body, outline="")
    # ears / antenna
    cv.create_rectangle(*sc(10, 44, 18, 62), fill="#2b4a80", outline="")
    cv.create_rectangle(*sc(82, 44, 90, 62), fill="#2b4a80", outline="")
    cv.create_line(*sc(50, 18, 50, 6), fill="#2b4a80", width=max(1, int(2.4 * s)))
    cv.create_oval(*sc(45, 0, 55, 10), fill=T.WARN if mood == "cheer" else T.GOOD, outline="")
    # mortarboard
    cv.create_polygon(*sc(50, 4, 92, 20, 50, 34, 8, 20), fill="#1a2743", outline="")
    cv.create_line(*sc(84, 18, 84, 36), fill=T.WARN, width=max(1, int(2 * s)))
    cv.create_oval(*sc(80, 34, 89, 43), fill=T.WARN, outline="")
    # face plate
    cv.create_rectangle(*sc(26, 40, 74, 72), fill="#101726", outline="")
    # eyes
    eye_y, eye_h = (52, 6) if mood == "happy" else (50, 9)
    if mood == "happy" or mood == "cheer":
        cv.create_arc(*sc(31, 44, 47, 60), start=20, extent=140, style="arc",
                      outline=T.GOOD, width=max(1, int(2.6 * s)))
        cv.create_arc(*sc(53, 44, 69, 60), start=20, extent=140, style="arc",
                      outline=T.GOOD, width=max(1, int(2.6 * s)))
    else:
        look = -3 if mood == "think" else 0
        cv.create_oval(*sc(33, eye_y - eye_h / 2, 45, eye_y + eye_h / 2),
                       fill=T.GOOD, outline="")
        cv.create_oval(*sc(55, eye_y - eye_h / 2, 67, eye_y + eye_h / 2),
                       fill=T.GOOD, outline="")
        cv.create_oval(*sc(37 + look, eye_y - 2, 41 + look, eye_y + 2),
                       fill="#101726", outline="")
        cv.create_oval(*sc(59 + look, eye_y - 2, 63 + look, eye_y + 2),
                       fill="#101726", outline="")
    # glasses
    cv.create_oval(*sc(30, 44, 48, 60), outline="#7e8aa6", width=1)
    cv.create_oval(*sc(52, 44, 70, 60), outline="#7e8aa6", width=1)
    cv.create_line(*sc(48, 52, 52, 52), fill="#7e8aa6", width=1)
    # mouth
    if mood == "cheer":
        cv.create_oval(*sc(42, 62, 58, 72), fill=T.WARN, outline="")
    elif mood == "happy":
        cv.create_arc(*sc(38, 56, 62, 70), start=200, extent=140, style="arc",
                      outline=T.WARN, width=max(1, int(2.2 * s)))
    elif mood == "think":
        cv.create_line(*sc(42, 66, 54, 64), fill=T.WARN, width=max(1, int(2.2 * s)))
    else:
        cv.create_line(*sc(40, 65, 60, 65), fill=T.WARN, width=max(1, int(2.2 * s)))


class Typewriter:
    """Reveals dialogue a few characters at a time; click anywhere to finish."""

    def __init__(self, widget, root):
        self.widget = widget
        self.root = root
        self.job = None
        self.full = ""
        self.i = 0

    def play(self, text, speed=12, chunk=2):
        self.stop()
        self.full = text
        self.i = 0
        self.widget.configure(text="")
        self._tick(speed, chunk)

    def _tick(self, speed, chunk):
        if self.i >= len(self.full):
            self.job = None
            return
        self.i = min(len(self.full), self.i + chunk)
        self.widget.configure(text=self.full[:self.i])
        self.job = self.root.after(speed, lambda: self._tick(speed, chunk))

    def finish(self):
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
        self.widget.configure(text=self.full)

    def stop(self):
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None

    @property
    def running(self):
        return self.job is not None
