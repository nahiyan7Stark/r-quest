"""Colours, fonts and small look-and-feel helpers for R Quest.

Everything visual lives here so the game can be re-skinned without touching
any teaching content.
"""

# --- palette -------------------------------------------------------------
BG          = "#12161f"   # window background
PANEL       = "#1b2130"   # content panel
PANEL_ALT   = "#232b3d"   # secondary panel (context boxes)
BORDER      = "#2e3852"
INK         = "#e8ecf5"   # primary text
INK_DIM     = "#9aa6bf"   # secondary text
ACCENT      = "#6ea8ff"   # NPC / headings
ACCENT_DK   = "#2f6bd4"
GOOD        = "#59c98a"
WARN        = "#e8b463"
BAD         = "#e8737b"
CODE_BG     = "#0d1017"
CODE_INK    = "#b8f0c8"
R_BLUE      = "#7fb8ff"

# matplotlib figures are drawn on the panel colour so they sit flush in the UI
PLOT_BG     = PANEL
PLOT_INK    = INK
PLOT_GRID   = "#33405c"
SERIES = ["#6ea8ff", "#e8b463", "#59c98a", "#e8737b", "#b48ae8", "#5fd0d0"]

# --- fonts ---------------------------------------------------------------
# Tuples are (family, size, style). Families are chosen to exist on
# Windows / macOS / Linux; Tk silently substitutes if one is missing.
F_TITLE  = ("Georgia", 20, "bold")
F_H1     = ("Georgia", 15, "bold")
F_H2     = ("Segoe UI", 12, "bold")
F_BODY   = ("Segoe UI", 12)
F_SMALL  = ("Segoe UI", 10)
F_NPC    = ("Georgia", 13)
F_CODE   = ("Consolas", 11)
F_CODE_S = ("Consolas", 10)


def fallback_fonts(root):
    """Pick fonts that actually exist on this machine."""
    import tkinter.font as tkfont
    have = set(f.lower() for f in tkfont.families(root))

    def pick(*names):
        for n in names:
            if n.lower() in have:
                return n
        return "TkDefaultFont"

    serif = pick("Georgia", "Palatino", "Palatino Linotype", "DejaVu Serif",
                 "Times New Roman", "Liberation Serif")
    sans = pick("Segoe UI", "Helvetica Neue", "SF Pro Text", "DejaVu Sans",
                "Arial", "Liberation Sans")
    mono = pick("Consolas", "Menlo", "SF Mono", "DejaVu Sans Mono",
                "Courier New", "Liberation Mono")

    global F_TITLE, F_H1, F_H2, F_BODY, F_SMALL, F_NPC, F_CODE, F_CODE_S
    F_TITLE  = (serif, 20, "bold")
    F_H1     = (serif, 15, "bold")
    F_H2     = (sans, 12, "bold")
    F_BODY   = (sans, 12)
    F_SMALL  = (sans, 10)
    F_NPC    = (serif, 13)
    F_CODE   = (mono, 11)
    F_CODE_S = (mono, 10)
