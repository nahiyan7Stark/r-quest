#!/usr/bin/env python3
"""
================================================================================
 R QUEST  -  STAT 2500: Statistical Foundations for Data Analytics
 A guided learning game that teaches the whole course, in R, from zero.
================================================================================

 Run it with:      python main.py
 Needs:            Python 3.8+, plus pandas and matplotlib (pip install -r
                   requirements.txt).  Tkinter ships with Python on Windows and
                   macOS; on Linux it is the python3-tk package.
                   R itself is NOT required - the game computes everything and
                   shows you the exact R command that does the same job.

--------------------------------------------------------------------------------
 THE TEN LEVELS  (fixed order - each one leans on the ones before it)
--------------------------------------------------------------------------------
  1  Getting data into R          c(), <-, read.table()/read.csv() from a URL or
                                  a local file, table(), bar / pie / Pareto
  2  Describing data & outliers   summary(), var(), sd(), boxplot() and the
                                  1.5 IQR rule, z-scores, plot(x, y), sort/rank
  3  Discrete distributions       mean & variance of a discrete random variable,
                                  dbinom / pbinom, "at least / at most /
                                  between", dpois / ppois, plot(x, y, type = "h")
  4  The normal distribution      pnorm, qnorm, the d/p/q/r rule as ONE idea,
                                  empirical rule, IQR/s, qqnorm + qqline,
                                  normal approximation with continuity correction
  5  Sampling & the CLT           population vs sample vs sampling distribution,
                                  simulating means with a for loop, sigma/sqrt(n),
                                  the CLT seen and QQ-checked
  6  Confidence intervals         large-sample z interval, t.test()$conf.int,
                                  prop.test(), and why 90% is narrower than 95%
  7  One-sample hypothesis tests  H0 vs Ha in plain words, z-test, t.test(mu=),
                                  prop.test(p=), p-value vs alpha, and writing
                                  the conclusion as an English sentence
  8  Two-sample tests             independent z, pooled vs Welch t
                                  (var.equal), paired t, two-proportion test,
                                  and a decision tree for choosing between them
  9  Chi-square tests             observed vs expected, goodness of fit,
                                  test of independence, df and critical values
 10  Simple linear regression     lm(), reading summary(), confint(), and
                                  predict() - CONFIDENCE vs PREDICTION intervals

 BOSS CHALLENGE                   iris, held back from every level, plus one
                                  open question. Seven unscripted stages: load,
                                  describe, visualise, choose a test, run it,
                                  read it, and conclude in plain English.

--------------------------------------------------------------------------------
 FOR FUTURE EDITORS
--------------------------------------------------------------------------------
 rquest/steps.py       the seven step types a level is built from
 rquest/levels/*.py    pure content - no Tkinter anywhere in these files
 rquest/app.py         the window, the level map and the step runner
 rquest/ui.py          reusable widgets (cards, buttons, console pane, the NPC)
 rquest/rstats.py      statistics, printed exactly the way the R console prints
 rquest/distributions.py   normal/t/chi-square/F/binomial/Poisson in pure Python
 rquest/datasets.py    URL-first loading with a bundled offline fallback
 tools/verify.py       headless walk-through of every level and the boss

 To add a level: write levels/levelNN.py with a build() returning a Level, and
 add its title and goal to levels/__init__.py.  Nothing else needs touching.
================================================================================
"""

import sys


def _fail(msg):
    print("\n" + "=" * 70)
    print("R QUEST could not start.\n")
    print(msg)
    print("=" * 70 + "\n")
    sys.exit(1)


def main():
    if sys.version_info < (3, 8):
        _fail(f"Python 3.8 or newer is needed; this is {sys.version.split()[0]}.")

    try:
        import tkinter  # noqa: F401
    except ImportError:
        _fail("Tkinter is missing.\n\n"
              "  Windows / macOS : reinstall Python from python.org and make sure\n"
              "                    'tcl/tk and IDLE' is ticked.\n"
              "  Debian / Ubuntu : sudo apt install python3-tk\n"
              "  Fedora          : sudo dnf install python3-tkinter")

    missing = []
    for mod, pkg in (("pandas", "pandas"), ("matplotlib", "matplotlib"),
                     ("numpy", "numpy")):
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        _fail("These packages are missing: " + ", ".join(missing) + "\n\n"
              "Install them with:\n\n    pip install -r requirements.txt")

    from rquest.app import main as run
    run()


if __name__ == "__main__":
    main()
