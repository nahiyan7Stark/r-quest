"""Helpers shared by every level.

Two jobs:
  1. Give levels lazy access to data, so nothing is downloaded until the player
     actually reaches the step that needs it.
  2. Keep repeated content patterns (dataset notices, R command call-outs,
     "which function" distractor sets) in one place instead of copy-pasted
     through ten files.
"""

from __future__ import annotations

import textwrap

import numpy as np

from .. import datasets as DS
from .. import rstats as R


def data(key):
    """Lazily fetch a dataset; the loader caches, so repeat calls are free."""
    return DS.load(key)


def frame(key):
    return data(key).df


def offline_notice(key):
    """A short note telling the player where the numbers came from.

    Hard-wrapped, because it is printed inside the monospace console pane
    alongside R output, which must not be soft-wrapped.
    """
    ds = data(key)
    if ds.source == "url":
        return (f"Loaded live from the web:\n{ds.spec.url}\n"
                f"{len(ds.df)} rows, {len(ds.df.columns)} columns.")
    return textwrap.fill("OFFLINE COPY IN USE.  " + ds.notice, 74)


def src_line(key):
    ds = data(key)
    return ("live from the web" if ds.source == "url"
            else "from the bundled offline copy")


# --------------------------------------------------------------------------
# Reusable wrong-answer diagnoses.  These are the mistakes beginners actually
# make, so they get a real explanation rather than a red cross.
# --------------------------------------------------------------------------

DIAG_MEAN_FOR_TABLE = (
    r"\bmean\s*\(",
    "mean() averages numbers. The values here are words (categories), so there is "
    "nothing to average — R would give you NA and a warning. Counting is the job.")

DIAG_SUMMARY_FOR_TABLE = (
    r"\bsummary\s*\(",
    "summary() on a text column just tells you it is a character column and how long "
    "it is. To get counts of each category you need the counting function.")

DIAG_MISSING_DOLLAR = (
    r"^[^$]*\b(chol|mtcars|iris|d|df)\s*\)",
    "You passed the whole data frame instead of one column. R needs to know WHICH "
    "column — that is what the $ sign is for, as in chol$CHOL.")

DIAG_PLOT_RAW_CATEGORY = (
    r"barplot\s*\(\s*(chol\$)?[A-Za-z_.]+\s*\)",
    "barplot() expects a table of COUNTS, not the raw column. Feed the raw column to "
    "the counting function first, then pass that to barplot — the two are nested: "
    "barplot(table(...)).")

DIAG_EQUALS_COMPARISON = (
    r"==",
    "== is a comparison ('is this equal to that?'), which gives TRUE/FALSE. "
    "To store a value in a name, use <- instead.")


def quote_free(s):
    return s.replace('"', "").replace("'", "")


def pct(x, dp=1):
    return f"{100 * x:.{dp}f}%"


def counts_of(key, col):
    labs, cnt = R.table(frame(key)[col])
    return [str(l) for l in labs], list(cnt)


def num(key, col):
    return np.asarray(frame(key)[col], float)
