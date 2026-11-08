"""Headless walk-through of every level: renders each plot, resolves every
piece of lazily-computed text, and checks that each challenge's model answer
is actually accepted by the grader.  Run with:  python tools/verify.py
"""
import os, sys, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure

from rquest.levels import get_level, LEVEL_TITLES
from rquest.steps import resolve, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from rquest.grading import check

fails = []


def walk(n):
    L = get_level(n)
    kinds = {}
    for i, s in enumerate(L.steps):
        kinds[type(s).__name__] = kinds.get(type(s).__name__, 0) + 1
        where = f"L{n} step {i+1} {type(s).__name__}"
        try:
            if isinstance(s, Show):
                fig = Figure(figsize=(8.2, 4.2), dpi=80)
                s.draw(fig)
                assert fig.axes, "figure has no axes"
                resolve(s.caption)
            elif isinstance(s, RDemo):
                assert resolve(s.r_code).strip(), "empty R code"
                assert resolve(s.output).strip(), "empty output"
                resolve(s.note)
            elif isinstance(s, AskText):
                resolve(s.prompt); resolve(s.context); resolve(s.hint)
                fspec = s.free() if callable(s.free) else s.free
                spec = s.numeric() if callable(s.numeric) else s.numeric
                if fspec:
                    assert fspec.get("model"), "free-text step needs a model answer"
                    ok, msg = check(fspec["model"], s)
                elif spec:
                    ok, msg = check(f"{spec[0]:.6f}", s)
                else:
                    assert s.answers, "no model answer"
                    ok, msg = check(s.answers[0], s)
                assert ok, f"model answer rejected: {msg}"
                assert resolve(s.success).strip(), "empty success text"
                assert resolve(s.hint).strip(), "no hint"
                assert s.diagnoses or fspec, "no misconception diagnoses"
                for rx, m in s.diagnoses:
                    import re; re.compile(rx); assert m.strip()
            elif isinstance(s, AskChoice):
                resolve(s.prompt); resolve(s.context)
                assert len(s.options) == len(s.feedback), "option/feedback mismatch"
                assert 0 <= s.correct < len(s.options)
                for o in s.options: assert resolve(o).strip()
                for f in s.feedback: assert resolve(f).strip()
                resolve(s.success)
            elif isinstance(s, Recap):
                assert len(s.bullets) >= 3, "recap needs 3-5 bullets"
                assert len(s.bullets) <= 6
                for b in s.bullets: assert resolve(b).strip()
            elif isinstance(s, Explain):
                assert resolve(s.body).strip()
            elif isinstance(s, Say):
                assert resolve(s.text).strip()
        except Exception as e:
            fails.append(f"{where}: {e}")
            traceback.print_exc()
    need = {"Explain", "Show", "RDemo", "Recap"}
    missing = need - set(kinds)
    if missing:
        fails.append(f"L{n}: missing step types {missing}")
    if kinds.get("AskText", 0) + kinds.get("AskChoice", 0) < 2:
        fails.append(f"L{n}: fewer than 2 challenges")
    return kinds


def walk_boss():
    from rquest.levels.boss import build, STAGE_NAMES
    L = build()
    kinds = {}
    for i, s in enumerate(L.steps):
        kinds[type(s).__name__] = kinds.get(type(s).__name__, 0) + 1
        try:
            if isinstance(s, Show):
                fig = Figure(figsize=(8.2, 4.2), dpi=80); s.draw(fig)
                assert fig.axes; resolve(s.caption)
            elif isinstance(s, AskText):
                resolve(s.prompt); resolve(s.context); resolve(s.hint)
                fs = s.free() if callable(s.free) else s.free
                ns = s.numeric() if callable(s.numeric) else s.numeric
                if fs:
                    assert fs.get("model"); ok, m = check(fs["model"], s)
                elif ns:
                    ok, m = check(f"{ns[0]:.6f}", s)
                else:
                    ok, m = check(s.answers[0], s)
                assert ok, f"model answer rejected: {m}"
                resolve(s.success)
            elif isinstance(s, AskChoice):
                resolve(s.prompt); resolve(s.context)
                assert len(s.options) == len(s.feedback)
                for o in s.options: assert resolve(o).strip()
                for f in s.feedback: assert resolve(f).strip()
            elif isinstance(s, Explain):
                assert resolve(s.body).strip()
            elif isinstance(s, Say):
                assert resolve(s.text).strip()
        except Exception as e:
            fails.append(f"BOSS step {i+1} {type(s).__name__}: {e}")
            traceback.print_exc()
    stages = kinds.get("AskText", 0) + kinds.get("AskChoice", 0)
    if stages != len(STAGE_NAMES):
        fails.append(f"BOSS: {stages} interactive stages but "
                     f"{len(STAGE_NAMES)} stage names")
    return kinds


if __name__ == "__main__":
    only = [int(a) for a in sys.argv[1:]] or list(range(1, 11))
    for n in only:
        try:
            k = walk(n)
            print(f"L{n:>2} {LEVEL_TITLES[n]:<32} "
                  f"{sum(k.values()):>2} steps  " +
                  "  ".join(f"{a}:{b}" for a, b in sorted(k.items())))
        except Exception as e:
            fails.append(f"L{n}: failed to build: {e}")
            traceback.print_exc()
    if only == list(range(1, 11)):
        k = walk_boss()
        print(f"{'BOSS':>3} {'The Open Question':<32} {sum(k.values()):>2} steps  " +
              "  ".join(f"{a}:{b}" for a, b in sorted(k.items())))
    print()
    if fails:
        print("FAILURES:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("all checked levels pass")
