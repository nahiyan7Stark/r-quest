"""Dataset loading: live URL first, bundled copy as a silent safety net.

The teaching point of Level 1 is that R can read a file straight off the web,
so the game always *shows* the real read.table()/read.csv() URL command.  What
happens underneath is: try the URL with a short timeout, and if anything goes
wrong (no wifi, host down, campus proxy) fall back to the copy in data/ and
tell the player plainly that it is using the offline copy.  The lesson is
identical either way; only the bytes differ.
"""

from __future__ import annotations

import io
import os
import ssl
import urllib.request
from dataclasses import dataclass, field

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TIMEOUT = 6          # seconds -- long enough for a real fetch, short enough not to stall play


@dataclass
class Spec:
    key: str
    title: str
    url: str
    local: str
    r_command: str          # the exact R line the course would have you type
    sep: str = ","
    index_col: str | None = "rownames"
    blurb: str = ""
    offline_note: str = ""  # extra honesty when the bundled copy is not the real data


SPECS = {
    "chol": Spec(
        key="chol", title="Cholesterol study (300 adults)",
        url="https://assets.datacamp.com/blog_assets/chol.txt",
        local="chol.txt",
        r_command='chol <- read.table("https://assets.datacamp.com/blog_assets/chol.txt", header = TRUE)',
        sep=r"\s+", index_col=None,
        blurb="Age, height, weight, cholesterol, smoking habit, blood group and survival "
              "for 300 adults. The dataset used throughout the STAT 2500 labs.",
        offline_note="The bundled chol.txt is a simulated stand-in with the same columns "
                     "and realistic distributions, not the original 300 records.",
    ),
    "mtcars": Spec(
        key="mtcars", title="mtcars (1974 road tests, 32 cars)",
        url="https://vincentarelbundock.github.io/Rdatasets/csv/datasets/mtcars.csv",
        local="mtcars.csv",
        r_command="data(mtcars)   # built into R -- no download needed",
        blurb="Fuel consumption and 10 design/performance measures for 32 cars. "
              "Built into R itself, so it is the classic teaching set.",
    ),
    "iris": Spec(
        key="iris", title="iris (150 flowers, 3 species)",
        url="https://vincentarelbundock.github.io/Rdatasets/csv/datasets/iris.csv",
        local="iris.csv",
        r_command="data(iris)   # built into R -- no download needed",
        blurb="Petal and sepal measurements for 150 irises of three species. "
              "Good for group comparisons and regression.",
    ),
    "sleep": Spec(
        key="sleep", title="sleep (10 patients, 2 drugs)",
        url="https://vincentarelbundock.github.io/Rdatasets/csv/datasets/sleep.csv",
        local="sleep.csv",
        r_command="data(sleep)   # built into R -- no download needed",
        blurb="Extra hours of sleep gained by the SAME 10 patients on two different "
              "drugs. The textbook example of PAIRED data.",
    ),
    "tooth": Spec(
        key="tooth", title="ToothGrowth (60 guinea pigs)",
        url="https://vincentarelbundock.github.io/Rdatasets/csv/datasets/ToothGrowth.csv",
        local="ToothGrowth.csv",
        r_command="data(ToothGrowth)   # built into R -- no download needed",
        blurb="Tooth cell growth in 60 guinea pigs given vitamin C by orange juice (OJ) "
              "or ascorbic acid (VC), at three doses.",
    ),
}

# Datasets used inside the teaching levels.  `iris` is deliberately held back
# from all ten levels so the boss challenge really is on unseen data.
PRACTICE_KEYS = ["chol", "mtcars", "sleep", "tooth"]
BOSS_KEY = "iris"


@dataclass
class Dataset:
    spec: Spec
    df: pd.DataFrame
    source: str                  # "url" or "offline"
    notice: str = ""

    @property
    def key(self):
        return self.spec.key

    @property
    def title(self):
        return self.spec.title

    @property
    def r_command(self):
        return self.spec.r_command

    def r_head(self, n=6, cols=None):
        """Render the first n rows the way R's head() prints them."""
        d = self.df if cols is None else self.df[cols]
        return format_r_frame(d.head(n))


_cache: dict[str, Dataset] = {}


def _read(handle_or_path, spec) -> pd.DataFrame:
    df = pd.read_csv(handle_or_path, sep=spec.sep, engine="python")
    if spec.index_col and spec.index_col in df.columns:
        df = df.rename(columns={spec.index_col: "name"})
    return df


def load(key: str, force_offline: bool = False) -> Dataset:
    """Fetch a dataset, preferring the live URL.  Result is cached per session."""
    if key in _cache:
        return _cache[key]
    spec = SPECS[key]
    local_path = os.path.join(DATA_DIR, spec.local)

    if not force_offline:
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(spec.url, headers={"User-Agent": "R-Quest/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
                raw = r.read().decode("utf-8", "replace")
            df = _read(io.StringIO(raw), spec)
            if len(df) > 0:
                ds = Dataset(spec, df, "url", "")
                _cache[key] = ds
                return ds
        except Exception:
            pass       # any failure at all -> quietly use the bundled copy

    df = _read(local_path, spec)
    notice = ("Could not reach the web, so this is the bundled offline copy of "
              f"{spec.local}. Everything you learn here works identically on the live file. ")
    if spec.offline_note:
        notice += spec.offline_note
    ds = Dataset(spec, df, "offline", notice)
    _cache[key] = ds
    return ds


# --------------------------------------------------------------------------
# Printing helpers so on-screen output looks like the R console, not pandas.
# --------------------------------------------------------------------------

def _fmt_num(v, digits=4):
    if pd.isna(v):
        return "NA"
    if isinstance(v, (int,)) or (isinstance(v, float) and float(v).is_integer() and abs(v) < 1e9):
        return str(int(v))
    return f"{v:.{digits}g}"


def format_r_frame(df: pd.DataFrame, digits=4, max_rows=12) -> str:
    """Print a DataFrame roughly the way the R console prints a data.frame."""
    d = df.head(max_rows)
    cols = list(d.columns)
    body = [[_fmt_num(v, digits) if isinstance(v, (int, float)) else str(v)
             for v in row] for row in d.itertuples(index=False)]
    idx = [str(i + 1) for i in range(len(body))]
    widths = [max(len(idx[i]) for i in range(len(idx)))] if idx else [1]
    for j, c in enumerate(cols):
        w = len(str(c))
        for r in body:
            w = max(w, len(r[j]))
        widths.append(w)
    lines = [" " * widths[0] + "".join(" " + str(c).rjust(widths[j + 1])
                                       for j, c in enumerate(cols))]
    for i, r in enumerate(body):
        lines.append(idx[i].ljust(widths[0]) +
                     "".join(" " + r[j].rjust(widths[j + 1]) for j in range(len(cols))))
    if len(df) > max_rows:
        lines.append(f"... ({len(df) - max_rows} more rows)")
    return "\n".join(lines)


def format_r_vector(values, digits=4, per_line=10, names=None) -> str:
    """Print a vector the way R does, with [1] style position markers."""
    vals = [_fmt_num(v, digits) if isinstance(v, (int, float)) else str(v) for v in values]
    if names is not None:
        names = [str(n) for n in names]
        w = [max(len(a), len(b)) for a, b in zip(vals, names)]
        out = []
        for s in range(0, len(vals), per_line):
            e = s + per_line
            out.append(" ".join(names[i].rjust(w[i]) for i in range(s, min(e, len(vals)))))
            out.append(" ".join(vals[i].rjust(w[i]) for i in range(s, min(e, len(vals)))))
        return "\n".join(out)
    w = max((len(v) for v in vals), default=1)
    marker_w = len(f"[{max(1, len(vals) - per_line + 1)}]")
    out = []
    for s in range(0, len(vals), per_line):
        chunk = vals[s:s + per_line]
        out.append(f"[{s + 1}]".rjust(marker_w) + " " + " ".join(c.rjust(w) for c in chunk))
    return "\n".join(out)
