"""Level registry.

Levels are imported lazily so that starting the game is instant and a bug in
one level can never stop the others from loading.
"""

import importlib

LEVEL_TITLES = {
    1:  "Getting data into R",
    2:  "Describing data & outliers",
    3:  "Discrete distributions",
    4:  "The normal distribution",
    5:  "Sampling & the CLT",
    6:  "Confidence intervals",
    7:  "One-sample hypothesis tests",
    8:  "Two-sample tests",
    9:  "Chi-square tests",
    10: "Simple linear regression",
}

LEVEL_GOALS = {
    1:  "Read a file straight off the web, count categories with table(), and draw bar, "
        "pie and Pareto charts.",
    2:  "Read summary(), var() and sd(), spot outliers on a boxplot and with z-scores, "
        "and plot two variables against each other.",
    3:  "Work out the mean and variance of a discrete random variable, and answer "
        "'at least / at most / between' questions with dbinom, pbinom, dpois and ppois.",
    4:  "Use pnorm and qnorm, learn the d/p/q/r rule that works for every distribution, "
        "and decide whether data is normal using a histogram, IQR/s and a QQ plot.",
    5:  "See why sample means pile up in a bell shape even when the population does not — "
        "the Central Limit Theorem, simulated.",
    6:  "Build z, t and proportion confidence intervals, and explain why a 90% interval "
        "is narrower than a 95% one.",
    7:  "State H0 and Ha in plain words, run z, t and proportion tests, and turn a "
        "p-value into an English sentence.",
    8:  "Compare two groups: large-sample z, pooled vs Welch t, paired t, and the "
        "two-proportion test — and know which one the situation calls for.",
    9:  "Test patterns in counts: goodness-of-fit and independence, with degrees of "
        "freedom and the critical value.",
    10: "Fit a line with lm(), read summary() output, and tell a CONFIDENCE interval "
        "apart from a PREDICTION interval.",
}

_cache = {}


def get_level(n: int):
    if n not in _cache:
        mod = importlib.import_module(f".level{n:02d}", __name__)
        _cache[n] = mod.build()
    return _cache[n]
