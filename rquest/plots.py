"""Reusable matplotlib figures, themed to sit inside the game window.

Level files call these to build the "here is what the concept looks like"
visual for each level.  Every function takes the Figure as its first argument
so the engine can hand it a canvas that is already the right size.
"""

from __future__ import annotations

import inspect

import numpy as np
from matplotlib.axes import Axes
from . import theme as T
from . import rstats as R
from . import distributions as D


# Matplotlib renamed two boxplot arguments: `labels` became `tick_labels` in
# 3.9 (and was removed in 3.11), and `vert` became `orientation` in 3.11.  The
# game supports matplotlib 3.4 upwards, so work out at import time which
# spelling this installation wants rather than pinning anyone to an old
# release.
_BOXPLOT_PARAMS = set(inspect.signature(Axes.boxplot).parameters)


def _boxplot_compat(labels, vertical):
    kw = {}
    if labels is not None:
        kw["tick_labels" if "tick_labels" in _BOXPLOT_PARAMS else "labels"] = labels
    if "orientation" in _BOXPLOT_PARAMS:
        kw["orientation"] = "vertical" if vertical else "horizontal"
    else:
        kw["vert"] = bool(vertical)
    return kw


def style_axes(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(T.PLOT_BG)
    for sp in ax.spines.values():
        sp.set_color(T.PLOT_GRID)
    ax.tick_params(colors=T.INK_DIM, labelsize=9)
    ax.grid(True, color=T.PLOT_GRID, lw=0.6, alpha=0.55)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, color=T.INK, fontsize=11, pad=9)
    if xlabel:
        ax.set_xlabel(xlabel, color=T.INK_DIM, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=T.INK_DIM, fontsize=10)
    return ax


def new_axes(fig, title="", xlabel="", ylabel=""):
    fig.patch.set_facecolor(T.PLOT_BG)
    ax = fig.add_subplot(111)
    return style_axes(ax, title, xlabel, ylabel)


# --- Level 1: categorical ------------------------------------------------

def barplot(fig, labels, counts, title="", xlabel="", ylabel="Frequency"):
    ax = new_axes(fig, title, xlabel, ylabel)
    ax.bar(range(len(labels)), counts,
           color=[T.SERIES[i % len(T.SERIES)] for i in range(len(labels))],
           edgecolor=T.PLOT_BG, lw=1.2)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    for i, c in enumerate(counts):
        ax.text(i, c, str(c), ha="center", va="bottom", color=T.INK, fontsize=9)
    return ax


def piechart(fig, labels, counts, title=""):
    fig.patch.set_facecolor(T.PLOT_BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(T.PLOT_BG)
    total = sum(counts)
    w, txt, atxt = ax.pie(
        counts, labels=labels, autopct=lambda p: f"{p:.1f}%",
        colors=[T.SERIES[i % len(T.SERIES)] for i in range(len(labels))],
        wedgeprops=dict(edgecolor=T.PLOT_BG, lw=1.5), startangle=90)
    for t in txt:
        t.set_color(T.INK)
        t.set_fontsize(10)
    for t in atxt:
        t.set_color("#0d1017")
        t.set_fontsize(9)
    ax.set_title(title, color=T.INK, fontsize=11)
    return ax


def pareto(fig, labels, counts, title="Pareto diagram"):
    """Bars sorted tallest-first, with the running cumulative % on top."""
    order = np.argsort(counts)[::-1]
    labels = [labels[i] for i in order]
    counts = [counts[i] for i in order]
    ax = new_axes(fig, title, "", "Frequency")
    ax.bar(range(len(labels)), counts, color=T.SERIES[0], edgecolor=T.PLOT_BG, lw=1.2)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    cum = np.cumsum(counts) / sum(counts) * 100
    ax2 = ax.twinx()
    ax2.plot(range(len(labels)), cum, color=T.WARN, marker="o", lw=2)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("Cumulative %", color=T.WARN, fontsize=10)
    ax2.tick_params(colors=T.WARN, labelsize=9)
    ax2.grid(False)
    for sp in ax2.spines.values():
        sp.set_color(T.PLOT_GRID)
    for i, c in enumerate(cum):
        ax2.text(i, c + 4, f"{c:.0f}%", ha="center", color=T.WARN, fontsize=8)
    return ax


# --- Level 2: description and outliers -----------------------------------

def histogram(fig, x, bins=15, title="", xlabel="", ylabel="Frequency",
              show_normal=False, color=None):
    ax = new_axes(fig, title, xlabel, ylabel)
    x = np.asarray(x, float)
    n, b, patches = ax.hist(x, bins=bins, color=color or T.SERIES[0],
                            edgecolor=T.PLOT_BG, lw=1.0, alpha=0.92)
    if show_normal:
        xs = np.linspace(x.min(), x.max(), 250)
        width = b[1] - b[0]
        m_, s_ = x.mean(), R.sd(x)
        ax.plot(xs, np.array([D.norm_pdf(v, m_, s_) for v in xs]) * len(x) * width,
                color=T.WARN, lw=2, label="normal curve with the same mean and sd")
        ax.legend(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID,
                  labelcolor=T.INK, fontsize=8, loc="upper right")
    return ax


def boxplot(fig, data, labels=None, title="", ylabel="", vertical=True):
    ax = new_axes(fig, title, "", ylabel)
    if not isinstance(data, (list, tuple)) or np.ndim(data[0]) == 0:
        data = [np.asarray(data, float)]
        labels = labels or [""]
    bp = ax.boxplot(data, patch_artist=True, widths=0.45,
                    **_boxplot_compat(labels, vertical),
                    medianprops=dict(color=T.WARN, lw=2),
                    flierprops=dict(marker="o", markerfacecolor=T.BAD,
                                    markeredgecolor=T.BAD, markersize=5, alpha=0.85),
                    whiskerprops=dict(color=T.INK_DIM),
                    capprops=dict(color=T.INK_DIM))
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(T.SERIES[i % len(T.SERIES)])
        patch.set_alpha(0.55)
        patch.set_edgecolor(T.INK_DIM)
    return ax


def scatter(fig, x, y, title="", xlabel="", ylabel="", line=None, annotate=None):
    ax = new_axes(fig, title, xlabel, ylabel)
    ax.scatter(x, y, s=32, color=T.SERIES[0], alpha=0.8, edgecolor=T.PLOT_BG, lw=0.6)
    if line is not None:
        b0, b1 = line
        xs = np.linspace(min(x), max(x), 100)
        ax.plot(xs, b0 + b1 * xs, color=T.WARN, lw=2.2,
                label=f"y = {R.sig(b0,4)} + {R.sig(b1,4)}x")
        ax.legend(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID,
                  labelcolor=T.INK, fontsize=9)
    if annotate:
        ax.text(0.02, 0.97, annotate, transform=ax.transAxes, va="top", ha="left",
                color=T.INK_DIM, fontsize=9,
                bbox=dict(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID, pad=5))
    return ax


def zscore_strip(fig, x, name="value", threshold=3.0):
    """Raw values on top, the same values as z-scores below, outliers flagged."""
    fig.patch.set_facecolor(T.PLOT_BG)
    x = np.asarray(x, float)
    z = R.zscores(x)
    ax1 = style_axes(fig.add_subplot(211), f"Raw {name}", "", "")
    ax2 = style_axes(fig.add_subplot(212), "Same data as z-scores (how many sd from the mean)", "z", "")
    flag = np.abs(z) > threshold
    ax1.scatter(x[~flag], np.zeros(int((~flag).sum())), s=26, color=T.SERIES[0], alpha=0.6)
    ax1.scatter(x[flag], np.zeros(int(flag.sum())), s=70, color=T.BAD, marker="D", zorder=3)
    ax1.axvline(x.mean(), color=T.WARN, lw=1.6, ls="--")
    ax1.set_yticks([])
    ax2.scatter(z[~flag], np.zeros(int((~flag).sum())), s=26, color=T.SERIES[0], alpha=0.6)
    ax2.scatter(z[flag], np.zeros(int(flag.sum())), s=70, color=T.BAD, marker="D", zorder=3,
                label=f"|z| > {threshold:g}: flagged as outliers")
    for t in (-threshold, threshold):
        ax2.axvline(t, color=T.BAD, lw=1.4, ls=":")
    ax2.axvline(0, color=T.WARN, lw=1.6, ls="--")
    ax2.set_yticks([])
    ax2.legend(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID, labelcolor=T.INK,
               fontsize=9, loc="upper right")
    fig.tight_layout()
    return ax2


# --- Levels 3-4: distributions -------------------------------------------

def discrete_dist(fig, ks, probs, title="", xlabel="x", ylabel="P(X = x)",
                  highlight=None, highlight_label=""):
    ax = new_axes(fig, title, xlabel, ylabel)
    cols = [T.SERIES[0]] * len(ks)
    if highlight is not None:
        hs = set(highlight)
        cols = [T.WARN if k in hs else T.SERIES[0] for k in ks]
    ax.bar(ks, probs, color=cols, edgecolor=T.PLOT_BG, lw=1.0, width=0.75)
    ax.set_xticks(list(ks))
    if highlight is not None and highlight_label:
        tot = sum(p for k, p in zip(ks, probs) if k in set(highlight))
        ax.text(0.98, 0.95, f"{highlight_label}\n= {R.sig(tot, 4)}",
                transform=ax.transAxes, ha="right", va="top", color=T.WARN, fontsize=10,
                bbox=dict(facecolor=T.PANEL_ALT, edgecolor=T.WARN, pad=5))
    return ax


def normal_curve(fig, mean=0, sd=1, shade=None, title="", xlabel="x",
                 label=None, mark=None):
    """Bell curve with an optional shaded tail/region -- shade=(lo, hi)."""
    ax = new_axes(fig, title, xlabel, "density")
    xs = np.linspace(mean - 4 * sd, mean + 4 * sd, 500)
    ys = np.array([D.norm_pdf(v, mean, sd) for v in xs])
    ax.plot(xs, ys, color=T.SERIES[0], lw=2.2)
    if shade is not None:
        lo = mean - 4 * sd if shade[0] is None else shade[0]
        hi = mean + 4 * sd if shade[1] is None else shade[1]
        m = (xs >= lo) & (xs <= hi)
        ax.fill_between(xs[m], 0, ys[m], color=T.WARN, alpha=0.45)
        area = D.norm_cdf(hi, mean, sd) - D.norm_cdf(lo, mean, sd)
        ax.text(0.02, 0.95, (label or "shaded area") + f" = {R.sig(area, 4)}",
                transform=ax.transAxes, va="top", color=T.WARN, fontsize=10,
                bbox=dict(facecolor=T.PANEL_ALT, edgecolor=T.WARN, pad=5))
    if mark is not None:
        for v in np.atleast_1d(mark):
            ax.axvline(v, color=T.BAD, lw=1.6, ls="--")
    ax.set_ylim(bottom=0)
    return ax


def empirical_rule_plot(fig, x, name=""):
    ax = new_axes(fig, f"Empirical rule check{': ' + name if name else ''}",
                  name or "value", "Frequency")
    x = np.asarray(x, float)
    m, s = x.mean(), R.sd(x)
    ax.hist(x, bins=22, color=T.SERIES[0], edgecolor=T.PLOT_BG, alpha=0.85)
    pcts = R.empirical_rule(x)
    for k, col, target in zip((1, 2, 3), (T.GOOD, T.WARN, T.BAD), (68, 95, 99.7)):
        ax.axvline(m - k * s, color=col, ls="--", lw=1.4)
        ax.axvline(m + k * s, color=col, ls="--", lw=1.4)
    txt = "\n".join(
        f"within {k} sd:  {pcts[k-1]*100:5.1f}%   (normal says {t}%)"
        for k, t in zip((1, 2, 3), (68, 95, 99.7)))
    ax.text(0.02, 0.97, txt, transform=ax.transAxes, va="top", family="monospace",
            color=T.INK, fontsize=9,
            bbox=dict(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID, pad=6))
    return ax


def qqplot(fig, x, title="Normal Q-Q Plot"):
    ax = new_axes(fig, title, "Theoretical Quantiles", "Sample Quantiles")
    x = np.asarray(x, float)
    osr = np.sort(x)                       # sample quantiles, as qqnorm() plots
    osm = np.array(D.qq_theoretical(len(x)))
    ax.scatter(osm, osr, s=22, color=T.SERIES[0], alpha=0.8)
    q1, q3 = R.quantile(x, .25), R.quantile(x, .75)
    tq1, tq3 = D.norm_ppf(.25), D.norm_ppf(.75)
    slope = (q3 - q1) / (tq3 - tq1)
    inter = q1 - slope * tq1
    xs = np.array([osm.min(), osm.max()])
    ax.plot(xs, inter + slope * xs, color=T.WARN, lw=2)
    return ax


# --- Level 5: CLT ---------------------------------------------------------

def clt_panels(fig, population, sample_means, n, pop_name="population"):
    fig.patch.set_facecolor(T.PLOT_BG)
    ax1 = style_axes(fig.add_subplot(121), f"The {pop_name} itself", "value", "count")
    ax1.hist(population, bins=30, color=T.SERIES[3], edgecolor=T.PLOT_BG, alpha=0.9)
    ax2 = style_axes(fig.add_subplot(122),
                     f"Means of 1000 samples of n = {n}", "sample mean", "count")
    ax2.hist(sample_means, bins=30, color=T.SERIES[0], edgecolor=T.PLOT_BG, alpha=0.9)
    xs = np.linspace(min(sample_means), max(sample_means), 200)
    w = (max(sample_means) - min(sample_means)) / 30
    mm, ss = float(np.mean(sample_means)), R.sd(sample_means)
    ax2.plot(xs, np.array([D.norm_pdf(v, mm, ss) for v in xs]) * len(sample_means) * w,
             color=T.WARN, lw=2)
    fig.tight_layout()
    return ax2


# --- Level 6: confidence intervals ---------------------------------------

def ci_ladder(fig, intervals, truth=None, title="", xlabel=""):
    """intervals: list of (lo, hi, centre, covers)."""
    ax = new_axes(fig, title, xlabel, "sample #")
    for i, (lo, hi, c, ok) in enumerate(intervals):
        col = T.SERIES[0] if ok else T.BAD
        ax.plot([lo, hi], [i, i], color=col, lw=2, alpha=0.9)
        ax.plot([c], [i], marker="o", ms=3.5, color=col)
    if truth is not None:
        ax.axvline(truth, color=T.WARN, lw=2, ls="--", label="true population value")
        ax.legend(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID,
                  labelcolor=T.INK, fontsize=9, loc="lower right")
    return ax


def ci_width_compare(fig, mean, se, levels=(0.90, 0.95, 0.99)):
    ax = new_axes(fig, "Same data, three confidence levels", "value", "")
    for i, lv in enumerate(levels):
        z = R.qnorm(1 - (1 - lv) / 2)
        lo, hi = mean - z * se, mean + z * se
        ax.plot([lo, hi], [i, i], lw=6, color=T.SERIES[i], alpha=0.85, solid_capstyle="butt")
        ax.text(hi, i + 0.16, f"  {int(lv*100)}%  width {R.sig(hi-lo,4)}   z* = {R.sig(z,4)}",
                va="center", color=T.INK, fontsize=9)
    ax.axvline(mean, color=T.WARN, ls="--", lw=1.6)
    ax.set_yticks(range(len(levels)))
    ax.set_yticklabels([f"{int(l*100)}%" for l in levels])
    ax.set_ylim(-0.6, len(levels) - 0.1)
    return ax


# --- Levels 7-8: hypothesis tests ----------------------------------------

def test_curve(fig, stat, df=None, alpha=0.05, two_sided=True, title="",
               dist_label="z"):
    """The decision picture: rejection region shaded, test statistic marked."""
    pdf = (lambda v: D.norm_pdf(v)) if df is None else (lambda v: D.t_pdf(v, df))
    ppf = (lambda q: D.norm_ppf(q)) if df is None else (lambda q: D.t_ppf(q, df))
    ax = new_axes(fig, title, f"{dist_label} value", "density")
    lim = max(4.0, abs(stat) * 1.25)
    xs = np.linspace(-lim, lim, 600)
    ys = np.array([pdf(v) for v in xs])
    ax.plot(xs, ys, color=T.SERIES[0], lw=2.2)
    if two_sided:
        crit = ppf(1 - alpha / 2)
        for lo, hi in ((-lim, -crit), (crit, lim)):
            m = (xs >= lo) & (xs <= hi)
            ax.fill_between(xs[m], 0, ys[m], color=T.BAD, alpha=0.38)
        ax.axvline(crit, color=T.BAD, lw=1.2, ls=":")
        ax.axvline(-crit, color=T.BAD, lw=1.2, ls=":")
        crit_txt = f"critical values  {chr(177)}{R.sig(crit,4)}"
    else:
        crit = ppf(1 - alpha)
        m = xs >= crit
        ax.fill_between(xs[m], 0, ys[m], color=T.BAD, alpha=0.38)
        ax.axvline(crit, color=T.BAD, lw=1.2, ls=":")
        crit_txt = f"critical value  {R.sig(crit,4)}"
    ax.axvline(stat, color=T.WARN, lw=2.4)
    ax.text(stat, ax.get_ylim()[1] * 0.92, f"  {dist_label} = {R.sig(stat,4)}",
            color=T.WARN, fontsize=10, ha="left" if stat < 0 else "right")
    ax.text(0.02, 0.97, f"red = reject H0 ({int(alpha*100)}% of the curve)\n{crit_txt}",
            transform=ax.transAxes, va="top", color=T.INK_DIM, fontsize=9,
            bbox=dict(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID, pad=5))
    ax.set_ylim(bottom=0)
    return ax


def paired_lines(fig, before, after, labels=("before", "after"), title=""):
    ax = new_axes(fig, title, "", "value")
    for b, a in zip(before, after):
        ax.plot([0, 1], [b, a], color=T.SERIES[0] if a >= b else T.BAD,
                marker="o", ms=5, alpha=0.8, lw=1.4)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.25, 1.25)
    ax.text(0.5, 0.02, "each line is ONE subject measured twice",
            transform=ax.transAxes, ha="center", color=T.INK_DIM, fontsize=9)
    return ax


# --- Level 9: chi-square --------------------------------------------------

def obs_vs_exp(fig, labels, observed, expected, title="Observed vs expected counts"):
    ax = new_axes(fig, title, "", "count")
    idx = np.arange(len(labels))
    ax.bar(idx - 0.19, observed, width=0.38, color=T.SERIES[0], label="observed")
    ax.bar(idx + 0.19, expected, width=0.38, color=T.WARN, alpha=0.85, label="expected if H0 true")
    ax.set_xticks(idx)
    ax.set_xticklabels(labels)
    ax.legend(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID, labelcolor=T.INK, fontsize=9)
    return ax


def chisq_curve(fig, stat, df, alpha=0.05, title=""):
    ax = new_axes(fig, title or f"Chi-square distribution, df = {df}",
                  "chi-square value", "density")
    crit = D.chi2_ppf(1 - alpha, df)
    lim = max(crit * 1.6, stat * 1.25, df * 3)
    xs = np.linspace(0.01, lim, 600)
    ys = np.array([D.chi2_pdf(v, df) for v in xs])
    ax.plot(xs, ys, color=T.SERIES[0], lw=2.2)
    m = xs >= crit
    ax.fill_between(xs[m], 0, ys[m], color=T.BAD, alpha=0.38)
    ax.axvline(crit, color=T.BAD, ls=":", lw=1.3)
    ax.axvline(stat, color=T.WARN, lw=2.4)
    ax.text(0.98, 0.95,
            f"test statistic = {R.sig(stat,4)}\ncritical value  = {R.sig(crit,4)}   (df = {df})",
            transform=ax.transAxes, ha="right", va="top", family="monospace",
            color=T.INK, fontsize=9,
            bbox=dict(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID, pad=6))
    ax.set_ylim(bottom=0)
    return ax


def mosaic(fig, m, rowlabels, collabels, title=""):
    ax = new_axes(fig, title, "", "")
    m = np.asarray(m, float)
    rowtot = m.sum(1)
    x = 0.0
    total = m.sum()
    for i in range(len(rowlabels)):
        w = rowtot[i] / total
        y = 0.0
        for j in range(len(collabels)):
            h = m[i, j] / rowtot[i]
            ax.add_patch(__import__("matplotlib").patches.Rectangle(
                (x, y), w * 0.97, h * 0.985, facecolor=T.SERIES[j % len(T.SERIES)],
                edgecolor=T.PLOT_BG, alpha=0.85))
            if h > 0.08 and w > 0.08:
                ax.text(x + w * 0.48, y + h * 0.5, f"{int(m[i,j])}", ha="center",
                        va="center", color="#0d1017", fontsize=9)
            y += h
        ax.text(x + w * 0.48, -0.05, rowlabels[i], ha="center", color=T.INK, fontsize=9)
        x += w
    handles = [__import__("matplotlib").patches.Patch(
        facecolor=T.SERIES[j % len(T.SERIES)], label=str(collabels[j]))
        for j in range(len(collabels))]
    ax.legend(handles=handles, facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID,
              labelcolor=T.INK, fontsize=9, loc="upper left", bbox_to_anchor=(1.02, 1))
    fig.subplots_adjust(right=0.79, bottom=0.09, top=0.90)
    ax.set_xlim(0, 1.02)
    ax.set_ylim(-0.1, 1.02)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    return ax


# --- Level 10: regression -------------------------------------------------

def regression_bands(fig, m, xlabel="x", ylabel="y", title="",
                     show_conf=True, show_pred=True, at=None):
    """Fitted line with the two intervals drawn on top of each other, because
    seeing prediction bands sit OUTSIDE confidence bands is the whole lesson."""
    ax = new_axes(fig, title, xlabel, ylabel)
    x, y = m["x"], m["y"]
    ax.scatter(x, y, s=30, color=T.SERIES[0], alpha=0.75, edgecolor=T.PLOT_BG, lw=0.5)
    xs = np.linspace(min(x), max(x), 200)
    fit = m["b0"] + m["b1"] * xs
    ax.plot(xs, fit, color=T.WARN, lw=2.3, label="fitted line")
    if show_pred:
        lo = np.array([R.predict_lm(m, v, interval="prediction")[1] for v in xs])
        hi = np.array([R.predict_lm(m, v, interval="prediction")[2] for v in xs])
        ax.fill_between(xs, lo, hi, color=T.BAD, alpha=0.16,
                        label="95% PREDICTION band (one new individual)")
    if show_conf:
        lo = np.array([R.predict_lm(m, v, interval="confidence")[1] for v in xs])
        hi = np.array([R.predict_lm(m, v, interval="confidence")[2] for v in xs])
        ax.fill_between(xs, lo, hi, color=T.GOOD, alpha=0.32,
                        label="95% CONFIDENCE band (the average y)")
    if at is not None:
        ax.axvline(at, color=T.INK_DIM, ls=":", lw=1.3)
    ax.legend(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID, labelcolor=T.INK, fontsize=9)
    return ax


def residual_plot(fig, m, xlabel="fitted values"):
    ax = new_axes(fig, "Residuals vs fitted", xlabel, "residual")
    ax.scatter(m["fit"], m["resid"], s=30, color=T.SERIES[0], alpha=0.8)
    ax.axhline(0, color=T.WARN, lw=1.8, ls="--")
    return ax
