"""The game shell: window chrome, level map, step runner, boss runner.

One window, three regions that never move:
  * header   -- game title, where you are, XP and stars
  * sidebar  -- the ten-level map plus a progress bar, always visible
  * stage    -- the scrolling content area, Professor Byte's dialogue card
                and the action bar underneath it

Level modules describe content as a list of steps (see steps.py); everything
about how a step is drawn lives here, so adding a level never means touching
Tkinter code.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from . import theme as T
from . import ui
from .grading import check
from .progress import Progress, N_LEVELS
from .steps import (Say, Explain, Show, RDemo, AskText, AskChoice, Recap, resolve)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("R Quest - STAT 2500: Statistical Foundations for Data Analytics")
        self.configure(bg=T.BG)
        # Fit the window to whatever screen this actually is, then centre it -
        # a 1366x768 laptop gets a window that fits above the taskbar, and a
        # big monitor still gets a comfortable 1180x790.
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w = max(940, min(1180, sw - 80))
        h = max(660, min(790, sh - 90))
        self.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}+{max(0, (sh - h) // 3)}")
        self.minsize(940, 660)
        T.fallback_fonts(self)

        self.progress = Progress()
        self.wrapreg = ui.WrapRegistry()

        # level-runner state
        self.level = None
        self.idx = 0
        self.attempts = 0
        self.first_try = 0
        self.challenges = 0
        self.answered = False
        self._xp_shown = self.progress.xp

        self._build_chrome()
        self.bind("<Return>", self._on_return)
        self.bind("<Escape>", lambda e: self.show_home())
        self.show_home()

    # =====================================================================
    # chrome
    # =====================================================================
    def _build_chrome(self):
        head = tk.Frame(self, bg="#0e1219", height=62)
        head.pack(fill="x", side="top")
        head.pack_propagate(False)

        badge = tk.Canvas(head, width=38, height=38, bg="#0e1219", highlightthickness=0)
        badge.pack(side="left", padx=(16, 10))
        badge.create_oval(2, 2, 36, 36, fill=T.ACCENT_DK, outline=T.ACCENT, width=2)
        badge.create_text(19, 19, text="R", fill="#ffffff", font=(T.F_TITLE[0], 17, "bold"))

        left = tk.Frame(head, bg="#0e1219")
        left.pack(side="left", pady=9)
        tk.Label(left, text="R QUEST", bg="#0e1219", fg=T.INK,
                 font=(T.F_TITLE[0], 17, "bold")).pack(anchor="w")
        tk.Label(left, text="STAT 2500  -  Statistical Foundations for Data Analytics",
                 bg="#0e1219", fg=T.INK_DIM, font=(T.F_SMALL[0], 9)).pack(anchor="w")

        right = tk.Frame(head, bg="#0e1219")
        right.pack(side="right", padx=16)
        self.lbl_rank = tk.Label(right, text="", bg="#0e1219", fg=T.INK_DIM, font=T.F_SMALL)
        self.lbl_rank.pack(anchor="e")
        row = tk.Frame(right, bg="#0e1219")
        row.pack(anchor="e")
        self.lbl_xp = tk.Label(row, text="0 XP", bg="#0e1219", fg=T.WARN,
                               font=(T.F_H1[0], 14, "bold"))
        self.lbl_xp.pack(side="left")
        self.lbl_stars = tk.Label(row, text="", bg="#0e1219", fg=T.WARN, font=T.F_H2)
        self.lbl_stars.pack(side="left", padx=(12, 0))

        crumb = tk.Frame(head, bg="#182031")
        crumb.pack(side="right", padx=22, pady=16)
        self.lbl_where = tk.Label(crumb, text="", bg="#182031", fg=T.INK_DIM,
                                  font=(T.F_SMALL[0], 10), padx=12, pady=5)
        self.lbl_where.pack()

        body = tk.Frame(self, bg=T.BG)
        body.pack(fill="both", expand=True)

        # ---- sidebar: the level map ------------------------------------
        self.side = tk.Frame(body, bg="#0e1219", width=252)
        self.side.pack(side="left", fill="y")
        self.side.pack_propagate(False)
        tk.Label(self.side, text="LEVEL MAP", bg="#0e1219", fg=T.INK_DIM,
                 font=(T.F_SMALL[0], 9, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        foot = tk.Frame(self.side, bg="#0e1219")
        foot.pack(fill="x", side="bottom", pady=12, padx=16)

        self.map_holder = tk.Frame(self.side, bg="#0e1219")
        self.map_holder.pack(fill="both", expand=True, padx=10)
        self.bar_bg = tk.Canvas(foot, height=7, bg="#1b2130", highlightthickness=0)
        self.bar_bg.pack(fill="x")
        self.lbl_prog = tk.Label(foot, text="", bg="#0e1219", fg=T.INK_DIM,
                                 font=(T.F_SMALL[0], 9), anchor="w", justify="left",
                                 wraplength=205)
        self.lbl_prog.pack(fill="x", pady=(5, 8))
        ui.Button(foot, "Main menu", self.show_home, kind="ghost",
                  font=T.F_SMALL, pad=(10, 6)).pack(fill="x")

        # ---- stage ------------------------------------------------------
        stage = tk.Frame(body, bg=T.BG)
        stage.pack(side="left", fill="both", expand=True)

        self.content = ui.ScrollArea(stage, bg=T.BG)
        self.content.pack(fill="both", expand=True, padx=22, pady=(16, 6))
        self.content.on_width = self.wrapreg.apply

        # Professor Byte's dialogue card
        self.npc_card = tk.Frame(stage, bg=T.PANEL, highlightthickness=1,
                                 highlightbackground=T.BORDER)
        self.npc_card.pack(fill="x", padx=22, pady=(2, 6))
        self.npc_canvas = tk.Canvas(self.npc_card, width=76, height=92,
                                    bg=T.PANEL, highlightthickness=0)
        self.npc_canvas.pack(side="left", padx=(12, 6), pady=6)
        npc_txt = tk.Frame(self.npc_card, bg=T.PANEL)
        npc_txt.pack(side="left", fill="both", expand=True, pady=9, padx=(4, 14))
        tk.Label(npc_txt, text="PROFESSOR BYTE", bg=T.PANEL, fg=T.ACCENT,
                 font=(T.F_SMALL[0], 9, "bold"), anchor="w").pack(fill="x")
        self.npc_text = tk.Label(npc_txt, text="", bg=T.PANEL, fg=T.INK, font=T.F_NPC,
                                 justify="left", anchor="nw", wraplength=700, height=2)
        self.npc_text.pack(fill="both", expand=True, pady=(3, 0))
        self.wrapreg.add(self.npc_text, 190)
        self.typer = ui.Typewriter(self.npc_text, self)
        for w in (self.npc_card, self.npc_canvas, self.npc_text):
            w.bind("<Button-1>", lambda e: self.typer.finish())
        ui.draw_byte(self.npc_canvas, "talk", size=70)
        self._mood = "talk"
        self._blink()

        # action bar
        self.actions = tk.Frame(stage, bg=T.BG)
        self.actions.pack(fill="x", padx=22, pady=(0, 14))

        self._refresh_hud()

    def _blink(self):
        """A cheap sign of life: Byte blinks every few seconds."""
        if self._mood in ("talk", "think"):
            ui.draw_byte(self.npc_canvas, "happy", size=70)
            self.after(130, lambda: ui.draw_byte(self.npc_canvas, self._mood, size=70))
        self.after(5200, self._blink)

    def set_mood(self, mood):
        self._mood = mood
        ui.draw_byte(self.npc_canvas, mood, size=70)

    def say(self, text, mood="talk"):
        self.set_mood(mood)
        self.typer.play(resolve(text))

    # ---- HUD ------------------------------------------------------------
    def _refresh_hud(self, animate=False):
        p = self.progress
        self.lbl_rank.configure(text=f"Rank: {p.rank()}")
        self.lbl_stars.configure(text="★ " + f"{p.total_stars}/{N_LEVELS * 3}")
        if animate and p.xp != self._xp_shown:
            self._animate_xp(p.xp)
        else:
            self._xp_shown = p.xp
            self.lbl_xp.configure(text=f"{p.xp} XP")
        done = len(p.completed)
        self.lbl_prog.configure(
            text=f"{done} of {N_LEVELS} levels complete" +
                 ("\nboss cleared ✓" if p.boss_done else ""))
        self.bar_bg.delete("all")
        self.bar_bg.update_idletasks()
        w = max(1, self.bar_bg.winfo_width())
        frac = done / N_LEVELS
        self.bar_bg.create_rectangle(0, 0, w, 7, fill="#1b2130", outline="")
        if frac > 0:
            self.bar_bg.create_rectangle(0, 0, w * frac, 7, fill=T.GOOD, outline="")
        self._build_map()

    def _animate_xp(self, target):
        step = max(1, (target - self._xp_shown) // 8)

        def tick():
            if self._xp_shown < target:
                self._xp_shown = min(target, self._xp_shown + step)
                self.lbl_xp.configure(text=f"{self._xp_shown} XP")
                self.after(35, tick)
            else:
                self.lbl_xp.configure(text=f"{target} XP")
        tick()

    def _build_map(self):
        from .levels import LEVEL_TITLES
        for w in self.map_holder.winfo_children():
            w.destroy()
        cur = self.level.number if self.level else None
        for n in range(1, N_LEVELS + 1):
            done = n in self.progress.completed
            open_ = self.progress.unlocked(n)
            active = (cur == n)
            bg = "#1d2738" if active else "#0e1219"
            row = tk.Frame(self.map_holder, bg=bg)
            row.pack(fill="x", pady=1)
            mark = "✓" if done else ("▶" if active else ("•" if open_ else "┈"))
            col = T.GOOD if done else (T.ACCENT if active else (T.INK_DIM if open_ else "#4a5570"))
            tk.Label(row, text=f" {mark} ", bg=bg, fg=col, font=T.F_H2,
                     width=3).pack(side="left")
            # the star column is always reserved, so a title can never collide
            tk.Label(row, text=("★" * self.progress.stars.get(n, 0)).ljust(3),
                     bg=bg, fg=(T.WARN if done else bg), font=(T.F_SMALL[0], 8),
                     width=4, anchor="e").pack(side="right", padx=(2, 6))
            lbl = tk.Label(row, text=f"{n}. {LEVEL_TITLES[n]}", bg=bg,
                           fg=(T.INK if open_ else "#4a5570"),
                           font=(T.F_SMALL[0], 10, "bold" if active else "normal"),
                           anchor="w", justify="left", wraplength=146)
            lbl.pack(side="left", fill="x", expand=True, pady=3)
            if open_:
                for w in (row, lbl):
                    w.configure(cursor="hand2")
                    w.bind("<Button-1>", lambda e, k=n: self.start_level(k))
        # boss entry
        bopen = self.progress.boss_unlocked()
        bg = "#0e1219"
        row = tk.Frame(self.map_holder, bg=bg)
        row.pack(fill="x", pady=(10, 1))
        tk.Label(row, text=" ◆ ", bg=bg, fg=(T.WARN if bopen else "#4a5570"),
                 font=T.F_H2, width=3).pack(side="left")
        lbl = tk.Label(row, text="BOSS: The Open Question", bg=bg,
                       fg=(T.WARN if bopen else "#4a5570"),
                       font=(T.F_SMALL[0], 10, "bold"), anchor="w", wraplength=168)
        lbl.pack(side="left", fill="x", expand=True, pady=3)
        if self.progress.boss_done:
            tk.Label(row, text="✓", bg=bg, fg=T.GOOD, font=T.F_SMALL).pack(side="right", padx=6)
        if bopen:
            for w in (row, lbl):
                w.configure(cursor="hand2")
                w.bind("<Button-1>", lambda e: self.start_boss())

    # ---- action bar helpers --------------------------------------------
    def clear_actions(self):
        for w in self.actions.winfo_children():
            w.destroy()

    def primary(self, text, cmd, kind="primary"):
        b = ui.Button(self.actions, text, cmd, kind=kind)
        b.pack(side="right", padx=(8, 0))
        return b

    def secondary(self, text, cmd, kind="ghost"):
        b = ui.Button(self.actions, text, cmd, kind=kind, font=T.F_SMALL, pad=(13, 8))
        b.pack(side="right", padx=(8, 0))
        return b

    def _on_return(self, _=None):
        if self.typer.running:
            self.typer.finish()
            return
        if getattr(self, "_enter_action", None):
            self._enter_action()

    # ---- staggered reveal ----------------------------------------------
    def _stagger(self, delay=45):
        kids = list(self.content.inner.winfo_children())
        infos = []
        for k in kids:
            try:
                infos.append(k.pack_info())
                k.pack_forget()
            except tk.TclError:
                infos.append(None)

        def show(i):
            if i >= len(kids):
                return
            if infos[i] is not None:
                try:
                    kids[i].pack(**infos[i])
                except tk.TclError:
                    pass
            self.after(delay, lambda: show(i + 1))
        show(0)

    # =====================================================================
    # home screen
    # =====================================================================
    def show_home(self):
        from .levels import LEVEL_TITLES, LEVEL_GOALS
        self.level = None
        self.typer.stop()
        self.lbl_where.configure(text="Main menu")
        self.clear_actions()
        self.content.clear()
        self.wrapreg.items = [(self.npc_text, 190)]
        c = self.content.inner

        hero = ui.card(c, accent=T.WARN, bg=T.PANEL)
        ui.card_title(hero, "Learn the whole of STAT 2500 by playing it",
                      colour=T.INK, kicker="welcome")
        ui.body_text(hero,
                     "Ten levels, one per lab, in the order the course teaches them. Every level "
                     "explains the idea in ordinary words first, shows you a picture of it, runs "
                     "the real R command in front of you, and then hands you the keyboard.\n\n"
                     "You do not need any programming background. You do not need R installed "
                     "either — the game runs the statistics for you and shows you the exact R "
                     "command that does the same job, which is the command your course expects "
                     "you to be able to write.",
                     self.wrapreg)

        grid = ui.card(c, accent=T.ACCENT)
        ui.card_title(grid, "What you will be able to do", kicker="the ten levels")
        for n in range(1, N_LEVELS + 1):
            row = tk.Frame(grid, bg=T.PANEL)
            row.pack(fill="x", pady=3)
            done = n in self.progress.completed
            tk.Label(row, text=f" {n} ", bg=(T.GOOD if done else T.ACCENT_DK),
                     fg="#0d1017" if done else "#ffffff",
                     font=(T.F_SMALL[0], 10, "bold"), width=3).pack(side="left", anchor="n")
            box = tk.Frame(row, bg=T.PANEL)
            box.pack(side="left", fill="x", expand=True, padx=10)
            tk.Label(box, text=LEVEL_TITLES[n], bg=T.PANEL, fg=T.INK, font=T.F_H2,
                     anchor="w").pack(fill="x")
            lbl = tk.Label(box, text=LEVEL_GOALS[n], bg=T.PANEL, fg=T.INK_DIM,
                           font=T.F_SMALL, anchor="w", justify="left", wraplength=600)
            lbl.pack(fill="x")
            self.wrapreg.add(lbl, 230)

        tips = ui.card(c, accent=T.GOOD)
        ui.card_title(tips, "How to play", kicker="controls")
        ui.body_text(tips,
                     "•  Click Continue (or press Enter) to move through an explanation.\n"
                     "•  When a challenge appears, type the R command and press Check.\n"
                     "•  A wrong answer is never punished. Byte tells you what your command "
                     "would actually have done, and you try again.\n"
                     "•  Stuck three times? A Show me button appears and you keep going.\n"
                     "•  Click the level map on the left to replay any level you have finished.",
                     self.wrapreg)

        nxt = self._next_level()
        if self.progress.boss_unlocked() and not self.progress.boss_done:
            self.primary("Face the boss challenge  ◆", self.start_boss, kind="good")
            self.say("All ten levels down. There is one thing left: a dataset you have never "
                     "seen and a question nobody has broken into steps for you. Ready?", "cheer")
        else:
            self.primary(("Start Level 1  ▶" if nxt == 1 else f"Continue: Level {nxt}  ▶"),
                         lambda: self.start_level(nxt))
            if self.progress.xp == 0:
                self.say("Hello. I am Professor Byte, and I will be your teaching assistant for "
                         "the next few hours. We start from absolutely nothing — I will not "
                         "assume you have ever written a line of code.", "happy")
            else:
                self.say(f"Welcome back. You are on {self.progress.xp} XP and ranked "
                         f"{self.progress.rank()}. Level {nxt} is waiting whenever you are.", "happy")
        if self.progress.boss_done:
            self.secondary("Replay the boss", self.start_boss)
        if self.progress.xp > 0:
            self.secondary("Reset progress", self._reset)
        self._enter_action = lambda: self.start_level(self._next_level())
        self._refresh_hud()
        self._stagger()

    def _next_level(self):
        for n in range(1, N_LEVELS + 1):
            if n not in self.progress.completed:
                return n
        return N_LEVELS

    def _reset(self):
        if messagebox.askyesno("Reset progress",
                               "Clear all XP, stars and completed levels?"):
            self.progress.reset()
            self.show_home()

    # =====================================================================
    # level runner
    # =====================================================================
    def start_level(self, n):
        from .levels import get_level
        self.level = get_level(n)
        self.idx = 0
        self.first_try = 0
        self.results = []
        self.challenges = sum(1 for s in self.level.steps
                              if isinstance(s, (AskText, AskChoice)))
        self.lbl_where.configure(text=f"Level {n} of {N_LEVELS}")
        self._refresh_hud()
        self.render_step()

    def render_step(self):
        if self.idx >= len(self.level.steps):
            self.finish_level()
            return
        step = self.level.steps[self.idx]
        self.content.clear()
        self.clear_actions()
        self.wrapreg.items = [(self.npc_text, 190)]
        self.attempts = 0
        self.answered = False
        c = self.content.inner

        self._step_header(c)
        handler = {
            Say: self._r_say, Explain: self._r_explain, Show: self._r_show,
            RDemo: self._r_rdemo, AskText: self._r_asktext,
            AskChoice: self._r_askchoice, Recap: self._r_recap,
        }[type(step)]
        handler(c, step)
        self._stagger()

    def _step_header(self, c):
        lv = self.level
        bar = tk.Frame(c, bg=T.BG)
        bar.pack(fill="x", pady=(0, 10))
        tk.Label(bar, text=(f"{lv.kicker} {lv.number}" if lv.kicker == "LEVEL"
                            else lv.kicker), bg=T.BG, fg=T.WARN,
                 font=(T.F_SMALL[0], 9, "bold")).pack(side="left")
        tk.Label(bar, text="  •  " + lv.title, bg=T.BG, fg=T.INK,
                 font=T.F_H2).pack(side="left")
        total = len(lv.steps)
        tk.Label(bar, text=f"step {self.idx + 1} / {total}", bg=T.BG, fg=T.INK_DIM,
                 font=T.F_SMALL).pack(side="right")
        dots = tk.Frame(c, bg=T.BG)
        dots.pack(fill="x", pady=(0, 12))
        cv = tk.Canvas(dots, height=5, bg=T.BG, highlightthickness=0)
        cv.pack(fill="x")

        def paint(_=None):
            cv.delete("all")
            w = max(1, cv.winfo_width())
            seg = w / total
            for i in range(total):
                col = T.ACCENT if i <= self.idx else "#222b3d"
                cv.create_rectangle(i * seg + 1, 0, (i + 1) * seg - 1, 5,
                                    fill=col, outline="")
        cv.bind("<Configure>", paint)

    # ---- step renderers -------------------------------------------------
    def _advance(self):
        self.idx += 1
        self.render_step()

    def _cont(self, label="Continue  ▶"):
        self.primary(label, self._advance)
        self._enter_action = self._advance

    def _r_say(self, c, step):
        box = ui.card(c, accent=T.ACCENT, bg=T.PANEL_ALT)
        tk.Label(box, text="“", bg=T.PANEL_ALT, fg=T.ACCENT,
                 font=(T.F_TITLE[0], 30, "bold")).pack(anchor="w")
        ui.body_text(box, resolve(step.text), self.wrapreg, font=T.F_NPC)
        self.say(step.text, step.mood)
        self._cont()

    def _r_explain(self, c, step):
        box = ui.card(c, accent=T.GOOD)
        ui.card_title(box, step.title, kicker="the idea, in plain words")
        ui.body_text(box, resolve(step.body), self.wrapreg)
        ui.glossary(box, step.terms, self.wrapreg)
        self.say("Read this bit slowly — everything later leans on it.", "think")
        self._cont()

    def _r_show(self, c, step):
        box = ui.card(c, accent=T.WARN)
        ui.card_title(box, step.title, kicker="see it")
        fig = Figure(figsize=self._fig_size(step.tall), dpi=100)
        try:
            step.draw(fig)
        except Exception as e:                       # never let one plot kill the level
            ui.body_text(box, f"(This plot could not be drawn: {e})", self.wrapreg, fg=T.BAD)
        canvas = FigureCanvasTkAgg(fig, master=box)
        canvas.draw()
        w = canvas.get_tk_widget()
        w.configure(bg=T.PLOT_BG, highlightthickness=0)
        w.pack(fill="x", pady=(4, 8))
        ui.body_text(box, resolve(step.caption), self.wrapreg, fg=T.INK_DIM, font=T.F_SMALL)
        self.say("Have a proper look at this picture before you read on.", "think")
        self._cont()

    def _fig_size(self, tall=False):
        """Pick a figure size that fits the window without forcing a scroll.

        Measured from the live window rather than hard-coded, so the plots stay
        whole on a 768-pixel-tall laptop as well as a big monitor.
        """
        self.update_idletasks()
        h = self.content.canvas.winfo_height()
        w = self.content.canvas.winfo_width()
        if h < 60:                       # not laid out yet -- fall back on the window
            h = max(320, self.winfo_height() - 284)
            w = max(520, self.winfo_width() - 320)
        # Subtract what the card spends on chrome -- step header, kicker,
        # title, the caption underneath and the card's own padding -- so the
        # whole figure AND its caption fit without scrolling.  `tall` only
        # raises the ceiling, for players with a big monitor; it never lets a
        # figure spill past the fold on a short laptop screen.
        fig_h = max(215, min(h - 186, 470 if tall else 380))
        fig_w = max(440, min(w - 78, 900))
        return (fig_w / 100.0, fig_h / 100.0)

    def _r_rdemo(self, c, step):
        box = ui.card(c, accent=T.R_BLUE)
        ui.card_title(box, step.title, colour=T.R_BLUE, kicker="watch me do it — real R")
        ui.console(box, resolve(step.r_code), resolve(step.output))
        note = resolve(step.note)
        if note:
            ui.body_text(box, note, self.wrapreg, fg=T.INK_DIM, pad=(8, 0))
        self.say("This is the actual R command. Type it exactly like that in RStudio and you "
                 "get exactly that output.", "talk")
        self._cont()

    def _r_asktext(self, c, step):
        box = ui.card(c, accent=T.BAD)
        ui.card_title(box, "Your turn", colour=T.BAD, kicker="challenge")
        ctx = resolve(step.context)
        if ctx:
            ui.console(box, None, ctx, title="the situation")
        ui.body_text(box, resolve(step.prompt), self.wrapreg, pad=(8, 4))

        entry_wrap = tk.Frame(box, bg=T.CODE_BG, highlightthickness=1,
                              highlightbackground=T.BORDER)
        entry_wrap.pack(fill="x", pady=(8, 2))
        tk.Label(entry_wrap, text=(" > " if not step.free else " ✎ "), bg=T.CODE_BG,
                 fg=T.ACCENT, font=T.F_CODE).pack(side="left", anchor="n",
                                                  pady=(9 if step.free else 0))
        is_free = bool(step.free)
        if is_free:
            box_txt = tk.Text(entry_wrap, height=4, bg=T.CODE_BG, fg=T.INK,
                              insertbackground=T.INK, font=T.F_BODY, bd=0,
                              highlightthickness=0, relief="flat", wrap="word",
                              padx=6, pady=8)
            box_txt.pack(side="left", fill="both", expand=True, padx=(0, 8))

            class _Var:
                def get(_s):
                    return box_txt.get("1.0", "end").strip()

                def set(_s, v):
                    box_txt.delete("1.0", "end")
                    box_txt.insert("1.0", v)
            var = _Var()
            ent = box_txt
        else:
            var = tk.StringVar(value="")
            ent = tk.Entry(entry_wrap, textvariable=var, bg=T.CODE_BG, fg=T.CODE_INK,
                           insertbackground=T.CODE_INK, font=T.F_CODE, bd=0,
                           highlightthickness=0, relief="flat")
            ent.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        ent.focus_set()
        if step.placeholder:
            ui.body_text(box, f"format:  {step.placeholder}", self.wrapreg,
                         fg=T.INK_DIM, font=T.F_CODE_S, pad=(4, 0))
        self.fb_holder = tk.Frame(box, bg=T.PANEL)
        self.fb_holder.pack(fill="x")

        def submit():
            if self.answered:
                return
            ok, msg = check(var.get(), step)
            for w in self.fb_holder.winfo_children():
                w.destroy()
            if ok:
                self.answered = True
                gained = self.progress.award(self.attempts)
                if self.attempts == 0:
                    self.first_try += 1
                self.results.append((self.idx, self.attempts, False))
                ui.feedback(self.fb_holder, True,
                            resolve(step.success) + f"\n\n+{gained} XP", self.wrapreg)
                self.progress.save()
                self._refresh_hud(animate=True)
                self.say("Yes. That is the one.", "cheer")
                ent.configure(state="disabled")
                self.clear_actions()
                self._cont()
            else:
                self.attempts += 1
                ui.feedback(self.fb_holder, False, msg, self.wrapreg)
                self.say("Not that one — read what I wrote and have another go. "
                         "Wrong answers cost you nothing here.", "think")
                if not is_free:
                    ent.selection_range(0, "end")
                ent.focus_set()
                if self.attempts >= 3:
                    self._offer_answer(step, var, ent, submit)
            self.content.to_bottom()

        if not is_free:
            ent.bind("<Return>", lambda e: submit())
        else:
            ent.bind("<Control-Return>", lambda e: submit())
        self.primary("Check  ✓", submit, kind="good")
        if resolve(step.hint):
            self.secondary("Hint", lambda: self._hint(step))
        self._enter_action = None if is_free else submit

    def _offer_answer(self, step, var, ent, submit):
        if getattr(self, "_reveal_btn", None):
            return

        def reveal():
            fspec = step.free() if callable(step.free) else step.free
            spec = step.numeric() if callable(step.numeric) else step.numeric
            if step.answers:
                ans = step.answers[0]
            elif fspec:
                ans = fspec.get("model", "")
            else:
                ans = f"{spec[0]:.4g}" if spec else ""
            var.set(ans)
            ent.configure(state="normal")
            for w in self.fb_holder.winfo_children():
                w.destroy()
            ui.feedback(self.fb_holder, True,
                        f"The answer is:\n\n    {ans}\n\n{resolve(step.success)}\n\n"
                        "No XP for this one, but you have seen it now — that is what "
                        "matters. Onwards.", self.wrapreg)
            self.answered = True
            self.results.append((self.idx, 99, True))
            self.clear_actions()
            self._cont()
            self.say("No shame in that. Half of learning R is seeing the command once.", "talk")
            self.content.to_bottom()
        self._reveal_btn = self.secondary("Show me the answer", reveal, kind="quiet")

    def _hint(self, step):
        for w in self.fb_holder.winfo_children():
            w.destroy()
        ui.feedback(self.fb_holder, False, "HINT:  " + resolve(step.hint), self.wrapreg)
        self.say("Here is a nudge.", "think")
        self.content.to_bottom()

    def _r_askchoice(self, c, step):
        box = ui.card(c, accent=T.BAD)
        ui.card_title(box, "Your turn", colour=T.BAD, kicker="challenge")
        ctx = resolve(step.context)
        if ctx:
            ui.console(box, None, ctx, title="the situation")
        ui.body_text(box, resolve(step.prompt), self.wrapreg, pad=(8, 8))
        holder = tk.Frame(box, bg=T.PANEL)
        holder.pack(fill="x")
        self.fb_holder = tk.Frame(box, bg=T.PANEL)
        self.fb_holder.pack(fill="x")
        buttons = []

        def pick(i):
            if self.answered:
                return
            for w in self.fb_holder.winfo_children():
                w.destroy()
            if i == step.correct:
                self.answered = True
                gained = self.progress.award(self.attempts)
                if self.attempts == 0:
                    self.first_try += 1
                self.results.append((self.idx, self.attempts, False))
                for j, b in enumerate(buttons):
                    b.mark("right" if j == i else "off")
                ui.feedback(self.fb_holder, True,
                            resolve(step.success or step.feedback[i]) + f"\n\n+{gained} XP",
                            self.wrapreg)
                self.progress.save()
                self._refresh_hud(animate=True)
                self.say("Exactly right.", "cheer")
                self.clear_actions()
                self._cont()
            else:
                self.attempts += 1
                buttons[i].mark("wrong")
                ui.feedback(self.fb_holder, False, resolve(step.feedback[i]), self.wrapreg)
                self.say("Not that one. Look at what I said about it and pick again.", "think")
            self.content.to_bottom()

        for i, opt in enumerate(step.options):
            b = ui.OptionButton(holder, chr(65 + i), resolve(opt),
                                lambda k=i: pick(k), self.wrapreg)
            b.pack(fill="x", pady=4)
            buttons.append(b)
        self._enter_action = None

    def _r_recap(self, c, step):
        self.show_recap(step, on_close=self._advance)

    def show_recap(self, step, on_close):
        win = tk.Toplevel(self)
        win.title(step.title)
        win.configure(bg=T.PANEL)
        win.transient(self)
        win.resizable(False, False)
        head = tk.Frame(win, bg=T.GOOD)
        head.pack(fill="x")
        tk.Label(head, text=f"  {step.title.upper()}  -  " +
                 (f"LEVEL {self.level.number} CLEARED" if self.level.kicker == "LEVEL"
                  else f"{self.level.kicker} CLEARED"),
                 bg=T.GOOD, fg="#0d1017", font=(T.F_H2[0], 11, "bold"),
                 pady=8).pack(anchor="w")
        body = tk.Frame(win, bg=T.PANEL, padx=26, pady=20)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="What you should walk away with", bg=T.PANEL, fg=T.INK,
                 font=T.F_H1, anchor="w").pack(fill="x", pady=(0, 12))
        for b in step.bullets:
            row = tk.Frame(body, bg=T.PANEL)
            row.pack(fill="x", pady=5)
            tk.Label(row, text="▸", bg=T.PANEL, fg=T.GOOD,
                     font=T.F_H2).pack(side="left", anchor="n")
            tk.Label(row, text=resolve(b), bg=T.PANEL, fg=T.INK, font=T.F_BODY,
                     justify="left", anchor="w", wraplength=560).pack(side="left", padx=10)
        tk.Frame(body, bg=T.BORDER, height=1).pack(fill="x", pady=16)
        ui.Button(body, "Got it  ▶", lambda: (win.destroy(), on_close()),
                  kind="good").pack(anchor="e")
        self.say("Level done. Have a look at the recap and then we push on.", "cheer")
        win.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - win.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - win.winfo_height()) // 3
        win.geometry(f"+{max(0,x)}+{max(0,y)}")
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), on_close()))
        win.grab_set()
        win.focus_set()

    def finish_level(self):
        if self.level.on_finish is not None:
            hook = self.level.on_finish
            self.level = None
            hook(self)
            return
        n = self.level.number
        was_new = n not in self.progress.completed
        self.progress.finish_level(n, self.first_try, self.challenges)
        self._refresh_hud(animate=True)
        self.content.clear()
        self.clear_actions()
        self.wrapreg.items = [(self.npc_text, 190)]
        c = self.content.inner
        box = ui.card(c, accent=T.GOOD)
        stars = self.progress.stars.get(n, 1)
        tk.Label(box, text="★" * stars + "☆" * (3 - stars), bg=T.PANEL,
                 fg=T.WARN, font=(T.F_TITLE[0], 30, "bold")).pack(anchor="w")
        ui.card_title(box, f"Level {n} complete — {self.level.title}", colour=T.GOOD)
        ui.body_text(box, f"You got {self.first_try} of {self.challenges} challenges right on "
                          f"the first try.\n\n{self.level.goal}", self.wrapreg)
        nxt = n + 1
        if nxt <= N_LEVELS:
            self.primary(f"Level {nxt}  ▶", lambda: self.start_level(nxt))
            self._enter_action = lambda: self.start_level(nxt)
            self.say(f"Level {n} is behind us. {'Nicely done. ' if stars == 3 else ''}"
                     f"Level {nxt} builds straight on it.", "happy")
        elif self.progress.boss_unlocked():
            self.primary("The boss challenge  ◆", self.start_boss, kind="good")
            self._enter_action = self.start_boss
            self.say("That is all ten. Everything you need is now in your hands — "
                     "the boss is where you use it without me holding the map.", "cheer")
        self.secondary("Back to menu", self.show_home)
        self.level = None
        self._refresh_hud()
        self._stagger()

    # =====================================================================
    # boss
    # =====================================================================
    def start_boss(self):
        from .levels.boss import build as build_boss
        self.level = build_boss()
        self.idx = 0
        self.first_try = 0
        self.results = []
        self.challenges = sum(1 for s in self.level.steps
                              if isinstance(s, (AskText, AskChoice)))
        self.lbl_where.configure(text="BOSS CHALLENGE")
        self._refresh_hud()
        self.render_step()


def main():
    app = App()
    app.mainloop()
