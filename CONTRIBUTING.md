# Contributing

The most useful contributions, roughly in order:

1. **Tell me it broke.** Open an issue with the error text and what you were
   doing. Install problems count — if the instructions failed you, they will
   fail the next person.
2. **Tell me an explanation was confusing.** Which level, which step, what you
   expected it to say. This is worth more than code.
3. **Add a wrong-answer diagnosis.** If you typed something reasonable and the
   game gave you generic feedback, that is a gap. See below.
4. **Add or fix content.**

## How the project is laid out

Level files contain **content only** — no Tkinter anywhere. A level is a list of
steps, and `rquest/app.py` knows how to draw each kind. The seven step types are
in `rquest/steps.py`:

| Step | What it does |
|---|---|
| `Say` | Professor Byte speaks, 2–4 sentences |
| `Explain` | Plain-language concept panel, shown before any code |
| `Show` | A real matplotlib figure |
| `RDemo` | "Watch me do it": the exact R command and its output |
| `AskText` | Player types an R command, a number, or a sentence |
| `AskChoice` | Multiple choice, each option with its own diagnosis |
| `Recap` | End-of-level takeaways pop-up |

## Adding a wrong-answer diagnosis

This is the easiest useful change. Open the relevant `rquest/levels/levelNN.py`,
find the `AskText` step, and add a `(regex, message)` pair to its `diagnoses`
list. They are tried in order against what the player typed:

```python
diagnoses=[
    (r"\bmean\s*\(",
     "mean() averages numbers. These values are words, so there is nothing "
     "to average - R would give you NA. Counting is the job here."),
]
```

Write the message as **what their command would actually have done**, not as
"that is wrong".

## Adding a level

Write `rquest/levels/level11.py` with a `build()` returning a `Level`, then add
its title and goal to `rquest/levels/__init__.py`. Nothing else needs touching.

## Before you open a pull request

```bash
python tools/verify.py        # every level: plots render, model answers accepted
python tools/verify_stats.py  # every printed statistic still matches real R
python tools/playthrough.py   # plays the whole game through the real widgets
```

The first two run headless. The third needs a display; on a headless Linux box
use `xvfb-run -a python tools/playthrough.py`.

**`verify_stats.py` is the one that matters most.** The game's credibility rests
on its numbers being identical to R's, so if you touch `rstats.py` or
`distributions.py` and that script complains, the change is wrong.
