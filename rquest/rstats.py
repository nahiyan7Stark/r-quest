"""R-equivalent statistics, printed the way the R console prints them.

The game engine runs in Python, but the course is taught in R.  Every number
the player sees on screen is computed here and formatted to match what R would
actually print, so that what they read in the game is what they will read in
RStudio.  Where R and Python differ in convention (quantile type, denominator
of the variance, degrees of freedom for Welch) we follow R.
"""

from __future__ import annotations

import math
import numpy as np

from . import distributions as D


# --------------------------------------------------------------------------
# number formatting that matches R's `format(x, digits = k)`
# --------------------------------------------------------------------------

def sig(x, digits=4):
    """Significant-digit formatting, R style: 0.06063, 1.294e-10, 20.66333."""
    if x is None or (isinstance(x, float) and (math.isnan(x))):
        return "NA"
    if x == 0:
        return "0"
    ax = abs(x)
    if ax < 1e-4 or ax >= 1e5:
        s = f"{x:.{max(0, digits - 1)}e}"
        m, e = s.split("e")
        m = m.rstrip("0").rstrip(".")
        return f"{m}e{int(e):+03d}".replace("e+0", "e+").replace("e-0", "e-") \
            if abs(int(e)) < 100 else f"{m}e{int(e)}"
    d = max(0, digits - int(math.floor(math.log10(ax))) - 1)
    s = f"{x:.{d}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def fmt_common(values, digits=7):
    """Format a set of numbers the way R's format() does: one shared number of
    decimal places, chosen so every value still shows `digits` significant
    figures.  This is why R prints 10.40 15.43 19.20 -- not 10.4 15.43 19.2."""
    vals = [float(v) for v in values]
    need = 0
    for v in vals:
        if v == 0 or math.isnan(v):
            continue
        need = max(need, digits - 1 - int(math.floor(math.log10(abs(v)))))
    need = max(0, min(need, 15))
    out = [("NA" if math.isnan(v) else f"{v:.{need}f}") for v in vals]
    # drop a shared trailing-zero column if no value needs it
    while need > 0 and all(o.endswith("0") for o in out if o != "NA"):
        need -= 1
        out = [("NA" if math.isnan(v) else f"{v:.{need}f}") for v in vals]
    return out


def format_named(names, values) -> str:
    """Print a named vector the way R does: every column the same width, which
    is the widest name or value anywhere in the vector."""
    names = [str(n) for n in names]
    values = [str(v) for v in values]
    w = max([len(s) for s in names + values] or [1])
    return (" ".join(s.rjust(w) for s in names) + " \n" +
            " ".join(s.rjust(w) for s in values) + " ")


def pval_coef(p):
    """format.pval as printCoefmat uses it: '< 2e-16' rather than '< 2.2e-16'."""
    if p < 2e-16:
        return "< 2e-16"
    return sig(p, 3)


def fmt_fixed(values, decimals):
    """Round to a fixed number of decimals, then drop a trailing-zero column
    that no value in the group actually needs."""
    out = [f"{float(v):.{decimals}f}" for v in values]
    while decimals > 0 and all(o.endswith("0") for o in out):
        decimals -= 1
        out = [f"{float(v):.{decimals}f}" for v in values]
    return out


def pval(p, digits=4):
    """R prints small p-values as '< 2.2e-16'."""
    if p < 2.2e-16:
        return "< 2.2e-16"
    return sig(p, digits)


def stars(p):
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "** "
    if p < 0.05:
        return "*  "
    if p < 0.1:
        return ".  "
    return "   "


SIGNIF_CODES = ("---\nSignif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1")


# --------------------------------------------------------------------------
# Level 2: descriptive statistics
# --------------------------------------------------------------------------

def quantile(x, p):
    """R's default quantile (type 7) == numpy's default linear interpolation."""
    return float(np.quantile(np.asarray(x, dtype=float), p, method="linear"))


def var(x):
    """R's var(): divides by n-1."""
    return float(np.var(np.asarray(x, dtype=float), ddof=1))


def sd(x):
    return math.sqrt(var(x))


def summary(x, digits=4) -> str:
    """Reproduce R's summary() for a numeric vector."""
    a = np.asarray(x, dtype=float)
    vals = [a.min(), quantile(a, .25), np.median(a), a.mean(), quantile(a, .75), a.max()]
    labels = ["Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max."]
    cells = fmt_common(vals, digits)
    return format_named(labels, cells)


def table(values) -> tuple:
    """R's table(): sorted unique values with counts."""
    vals, counts = np.unique(np.asarray(values, dtype=object), return_counts=True)
    order = np.argsort([str(v) for v in vals])
    return [vals[i] for i in order], [int(counts[i]) for i in order]


def format_table(values, varname="") -> str:
    labs, counts = table(values)
    labs = [str(l) for l in labs]
    cnt = [str(c) for c in counts]
    head = f"{varname}\n" if varname else "\n"
    return head + format_named(labs, cnt)


def zscores(x):
    a = np.asarray(x, dtype=float)
    return (a - a.mean()) / sd(a)


def boxplot_outliers(x):
    """The points R's boxplot() draws as separate dots: beyond 1.5 x IQR."""
    a = np.asarray(x, dtype=float)
    q1, q3 = quantile(a, .25), quantile(a, .75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return a[(a < lo) | (a > hi)], lo, hi


# --------------------------------------------------------------------------
# Levels 3-4: distributions.  R's d/p/q/r family.
# --------------------------------------------------------------------------

def dbinom(k, n, p):
    return D.binom_pmf(k, n, p)


def pbinom(q, n, p, lower_tail=True):
    v = D.binom_cdf(q, n, p)
    return v if lower_tail else 1.0 - v


def dpois(k, lam):
    return D.pois_pmf(k, lam)


def ppois(q, lam, lower_tail=True):
    v = D.pois_cdf(q, lam)
    return v if lower_tail else 1.0 - v


def pnorm(q, mean=0.0, sd_=1.0, lower_tail=True):
    v = D.norm_cdf(q, mean, sd_)
    return v if lower_tail else 1.0 - v


def qnorm(p, mean=0.0, sd_=1.0):
    return D.norm_ppf(p, mean, sd_)


def qt(p, df):
    return D.t_ppf(p, df)


def pt(q, df, lower_tail=True):
    v = D.t_cdf(q, df)
    return v if lower_tail else 1.0 - v


def discrete_mean_var(values, probs):
    v = np.asarray(values, float)
    p = np.asarray(probs, float)
    mu = float((v * p).sum())
    var_ = float((v ** 2 * p).sum() - mu ** 2)
    return mu, var_


def iqr_over_s(x):
    a = np.asarray(x, float)
    return (quantile(a, .75) - quantile(a, .25)) / sd(a)


def empirical_rule(x):
    """Share of data within 1, 2 and 3 sd of the mean -- the 68/95/99.7 check."""
    a = np.asarray(x, float)
    m, s = a.mean(), sd(a)
    return [float(np.mean(np.abs(a - m) <= k * s)) for k in (1, 2, 3)]


# --------------------------------------------------------------------------
# Level 6-8: intervals and tests, printed as R prints them
# --------------------------------------------------------------------------

def _htest(title, data_line, stat_line, alt_line, conf=None, conf_level=0.95,
           estimates=None):
    out = ["", f"\t{title}", "", f"data:  {data_line}", stat_line]
    if alt_line:
        out.append(alt_line)
    if conf is not None:
        out.append(f"{int(round(conf_level * 100))} percent confidence interval:")
        lo, hi = fmt_common([conf[0], conf[1]], 7)
        out.append(f" {lo} {hi}")
    if estimates:
        out.append(format_named([n for n, _ in estimates],
                                fmt_common([v for _, v in estimates], 7)))
    out.append("")
    return "\n".join(out)


def z_interval(x, conf=0.95, sigma=None):
    """Large-sample z interval for a mean.  sigma=None -> estimate it with s."""
    a = np.asarray(x, float)
    n = len(a)
    s = sigma if sigma is not None else sd(a)
    z = qnorm(1 - (1 - conf) / 2)
    se = s / math.sqrt(n)
    return a.mean() - z * se, a.mean() + z * se, z, se, n, a.mean()


def _tp(t, df, alternative="two.sided"):
    """p-value for a t statistic, matching R's alternative= argument."""
    if alternative == "less":
        return D.t_cdf(t, df)
    if alternative == "greater":
        return 1.0 - D.t_cdf(t, df)
    return 2.0 * (1.0 - D.t_cdf(abs(t), df))


def t_test(x, y=None, mu=0.0, paired=False, var_equal=False, conf=0.95,
           alternative="two.sided", data_line="x", group_names=("x", "y")):
    """One-sample, two-sample (pooled or Welch) and paired t-tests.

    Degrees of freedom, the pooled/Welch standard error and the confidence
    interval all follow R's t.test() exactly, including Welch-Satterthwaite
    fractional df.
    """
    a = np.asarray(x, float)
    if y is not None and paired:
        b = np.asarray(y, float)
        d = a - b
        n = len(d)
        df = n - 1
        se = sd(d) / math.sqrt(n)
        tstat = (d.mean() - mu) / se
        centre = d.mean()
        title = "Paired t-test"
        alt_line = f"alternative hypothesis: true mean difference is not equal to {sig(mu)}"
        est = [("mean difference", d.mean())]
    elif y is not None:
        b = np.asarray(y, float)
        n1, n2 = len(a), len(b)
        v1, v2 = var(a), var(b)
        if var_equal:
            df = n1 + n2 - 2
            sp2 = ((n1 - 1) * v1 + (n2 - 1) * v2) / df
            se = math.sqrt(sp2 * (1 / n1 + 1 / n2))
            title = " Two Sample t-test"
        else:
            se = math.sqrt(v1 / n1 + v2 / n2)
            df = ((v1 / n1 + v2 / n2) ** 2
                  / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)))
            title = "Welch Two Sample t-test"
        centre = a.mean() - b.mean()
        tstat = (centre - mu) / se
        alt_line = ("alternative hypothesis: true difference in means between "
                    f"group {group_names[0]} and group {group_names[1]} is not equal to {sig(mu)}")
        est = [(f"mean in group {group_names[0]}", a.mean()),
               (f"mean in group {group_names[1]}", b.mean())]
    else:
        n = len(a)
        df = n - 1
        se = sd(a) / math.sqrt(n)
        tstat = (a.mean() - mu) / se
        centre = a.mean()
        title = "One Sample t-test"
        alt_line = f"alternative hypothesis: true mean is not equal to {sig(mu)}"
        est = [("mean of x", a.mean())]

    p = _tp(tstat, df, alternative)
    crit = qt(1 - (1 - conf) / 2, df)
    ci = (centre - crit * se, centre + crit * se)
    text = _htest(title, data_line,
                  f"t = {sig(tstat, 5)}, df = {sig(df, 5)}, p-value = {pval(p)}",
                  alt_line, ci, conf, est)
    return {"t": tstat, "df": df, "p": p, "conf_int": ci, "text": text, "se": se,
            "estimate": [v for _, v in est]}


def _alt(a):
    return {"two.sided": "two-sided", "less": "less", "greater": "greater"}.get(a, "two-sided")


def z_test(x, mu, sigma=None, conf=0.95, data_line="x", alternative="two.sided"):
    """One-sample z-test (BSDA::z.test style) for a large sample / known sigma."""
    a = np.asarray(x, float)
    n = len(a)
    s = sigma if sigma is not None else sd(a)
    se = s / math.sqrt(n)
    z = (a.mean() - mu) / se
    if alternative == "two.sided":
        p = 2 * (1 - D.norm_cdf(abs(z)))
    elif alternative == "greater":
        p = 1 - D.norm_cdf(z)
    else:
        p = D.norm_cdf(z)
    crit = qnorm(1 - (1 - conf) / 2)
    ci = (a.mean() - crit * se, a.mean() + crit * se)
    text = _htest("One-sample z-Test", data_line,
                  f"z = {sig(z, 5)}, p-value = {pval(p)}",
                  f"alternative hypothesis: true mean is not equal to {sig(mu)}",
                  ci, conf, [("mean of x", a.mean())])
    return {"z": z, "p": p, "conf_int": ci, "text": text, "se": se, "mean": a.mean()}


def z_test_two(x, y, sigma_x=None, sigma_y=None, conf=0.95,
               data_line="x and y", group_names=("x", "y")):
    """Two independent means, large samples (BSDA::zsum.test style)."""
    a, b = np.asarray(x, float), np.asarray(y, float)
    n1, n2 = len(a), len(b)
    s1 = sigma_x if sigma_x is not None else sd(a)
    s2 = sigma_y if sigma_y is not None else sd(b)
    se = math.sqrt(s1 ** 2 / n1 + s2 ** 2 / n2)
    diff = a.mean() - b.mean()
    z = diff / se
    p = 2 * (1 - D.norm_cdf(abs(z)))
    crit = qnorm(1 - (1 - conf) / 2)
    ci = (diff - crit * se, diff + crit * se)
    text = _htest("Two-sample z-Test", data_line,
                  f"z = {sig(z, 5)}, p-value = {pval(p)}",
                  "alternative hypothesis: true difference in means is not equal to 0",
                  ci, conf, [(f"mean of {group_names[0]}", a.mean()),
                             (f"mean of {group_names[1]}", b.mean())])
    return {"z": z, "p": p, "conf_int": ci, "text": text}


def prop_test(x, n, p=None, conf=0.95, correct=True, data_line=None):
    """R's prop.test for one or two proportions (Wilson interval, as R uses)."""
    if isinstance(x, (list, tuple, np.ndarray)):
        return _prop_test_two(list(x), list(n), conf, correct, data_line)
    ph = x / n
    p0 = p
    if p0 is None:
        p0 = 0.5
    cc = (0.5 / n) if correct else 0.0
    chi = (abs(ph - p0) - cc) ** 2 / (p0 * (1 - p0) / n)
    pv = 1 - D.chi2_cdf(chi, 1)
    ci = _wilson(x, n, conf, correct)
    title = ("1-sample proportions test with continuity correction" if correct
             else "1-sample proportions test without continuity correction")
    dl = data_line or f"{x} out of {n}, null probability {sig(p0)}"
    text = _htest(title, dl,
                  f"X-squared = {sig(chi, 5)}, df = 1, p-value = {pval(pv)}",
                  f"alternative hypothesis: true p is not equal to {sig(p0)}",
                  ci, conf, [("p", ph)])
    return {"chi": chi, "p": pv, "conf_int": ci, "estimate": ph, "text": text}


def _wilson(x, n, conf, correct):
    z = qnorm(1 - (1 - conf) / 2)
    ph = x / n
    cc = (0.5 / n) if correct else 0.0
    def bound(sign):
        pc = ph + sign * cc
        pc = min(max(pc, 0.0), 1.0)
        d = z * math.sqrt(pc * (1 - pc) / n + z * z / (4 * n * n))
        return (pc + z * z / (2 * n) + sign * d) / (1 + z * z / n)
    lo, hi = bound(-1), bound(1)
    return max(0.0, min(lo, hi)), min(1.0, max(lo, hi))


def _prop_test_two(xs, ns, conf, correct, data_line):
    x1, x2 = xs
    n1, n2 = ns
    p1, p2 = x1 / n1, x2 / n2
    pbar = (x1 + x2) / (n1 + n2)
    cc = (0.5 * (1 / n1 + 1 / n2)) if correct else 0.0
    num = abs(p1 - p2) - cc
    num = max(num, 0.0)
    chi = num ** 2 / (pbar * (1 - pbar) * (1 / n1 + 1 / n2))
    pv = 1 - D.chi2_cdf(chi, 1)
    z = qnorm(1 - (1 - conf) / 2)
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    d = p1 - p2
    lo, hi = d - (z * se + cc), d + (z * se + cc)
    title = ("2-sample test for equality of proportions with continuity correction"
             if correct else "2-sample test for equality of proportions without continuity correction")
    dl = data_line or f"c({x1}, {x2}) out of c({n1}, {n2})"
    text = _htest(title, dl,
                  f"X-squared = {sig(chi, 5)}, df = 1, p-value = {pval(pv)}",
                  "alternative hypothesis: two.sided",
                  (max(-1, lo), min(1, hi)), conf, [("prop 1", p1), ("prop 2", p2)])
    return {"chi": chi, "p": pv, "conf_int": (lo, hi), "estimate": (p1, p2), "text": text}


# --------------------------------------------------------------------------
# Level 9: chi-square
# --------------------------------------------------------------------------

def chisq_gof(observed, p=None, data_line="obs"):
    obs = np.asarray(observed, float)
    n = obs.sum()
    probs = np.full(len(obs), 1 / len(obs)) if p is None else np.asarray(p, float)
    exp = n * probs
    chi = float(((obs - exp) ** 2 / exp).sum())
    df = len(obs) - 1
    pv = 1.0 - D.chi2_cdf(chi, df)
    title = "Chi-squared test for given probabilities"
    text = _htest(title, data_line,
                  f"X-squared = {sig(chi, 5)}, df = {df}, p-value = {pval(pv)}", None)
    return {"chi": chi, "df": df, "p": pv, "expected": exp, "observed": obs,
            "critical": D.chi2_ppf(0.95, df), "text": text}


def chisq_independence(tbl, data_line="tbl"):
    obs = np.asarray(tbl, float)
    rt = obs.sum(1, keepdims=True)
    ct = obs.sum(0, keepdims=True)
    exp = rt @ ct / obs.sum()
    chi = float(((obs - exp) ** 2 / exp).sum())
    df = (obs.shape[0] - 1) * (obs.shape[1] - 1)
    pv = 1.0 - D.chi2_cdf(chi, df)
    text = _htest("Pearson's Chi-squared test", data_line,
                  f"X-squared = {sig(chi, 5)}, df = {df}, p-value = {pval(pv)}", None)
    return {"chi": float(chi), "df": int(df), "p": float(pv), "expected": exp,
            "observed": obs, "critical": D.chi2_ppf(0.95, df), "text": text}


def qchisq(p, df):
    return D.chi2_ppf(p, df)


def crosstab(a, b):
    """Contingency table plus its row/column labels, like R's table(a, b)."""
    ra = sorted(set(map(str, a)))
    rb = sorted(set(map(str, b)))
    m = np.zeros((len(ra), len(rb)), int)
    ia = {v: i for i, v in enumerate(ra)}
    ib = {v: i for i, v in enumerate(rb)}
    for x, y in zip(map(str, a), map(str, b)):
        m[ia[x], ib[y]] += 1
    return m, ra, rb


def format_crosstab(m, ra, rb, rowvar="", colvar="") -> str:
    m = np.asarray(m)
    body = [[str(v) for v in row] for row in m]
    rw = max([len(r) for r in ra] + [len(rowvar)])
    cw = [max([len(rb[j])] + [len(body[i][j]) for i in range(len(ra))]) for j in range(len(rb))]
    lines = []
    if colvar:
        lines.append(" " * rw + "  " + colvar)
    lines.append((rowvar.ljust(rw) if rowvar else " " * rw) +
                 "  " + " ".join(rb[j].rjust(cw[j]) for j in range(len(rb))))
    for i, r in enumerate(ra):
        lines.append(r.ljust(rw) + "  " + " ".join(body[i][j].rjust(cw[j]) for j in range(len(rb))))
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Level 10: simple linear regression
# --------------------------------------------------------------------------

def lm(x, y):
    """Least-squares fit of y ~ x, with everything summary(lm) reports."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    xbar, ybar = x.mean(), y.mean()
    sxx = float(((x - xbar) ** 2).sum())
    sxy = float(((x - xbar) * (y - ybar)).sum())
    b1 = sxy / sxx
    b0 = ybar - b1 * xbar
    fit = b0 + b1 * x
    resid = y - fit
    df = n - 2
    sse = float((resid ** 2).sum())
    sst = float(((y - ybar) ** 2).sum())
    s = math.sqrt(sse / df)                     # residual standard error
    se_b1 = s / math.sqrt(sxx)
    se_b0 = s * math.sqrt(1 / n + xbar ** 2 / sxx)
    t1, t0 = b1 / se_b1, b0 / se_b0
    p1 = 2 * (1 - D.t_cdf(abs(t1), df))
    p0 = 2 * (1 - D.t_cdf(abs(t0), df))
    r2 = 1 - sse / sst
    adj = 1 - (1 - r2) * (n - 1) / df
    fstat = (sst - sse) / (sse / df)
    pf = 1.0 - D.f_cdf(fstat, 1, df)
    return {"b0": b0, "b1": b1, "se_b0": se_b0, "se_b1": se_b1, "t0": t0, "t1": t1,
            "p0": p0, "p1": p1, "r2": r2, "adj_r2": adj, "s": s, "df": df, "n": n,
            "f": fstat, "pf": pf, "resid": resid, "fit": fit, "xbar": xbar,
            "sxx": sxx, "x": x, "y": y}


def format_lm_summary(m, formula="y ~ x", data="d", xname="x") -> str:
    r = np.sort(m["resid"])
    qs = [r.min(), quantile(r, .25), float(np.median(r)), quantile(r, .75), r.max()]
    rl = ["Min", "1Q", "Median", "3Q", "Max"]
    rv = fmt_common(qs, 4)

    rows = [("(Intercept)", m["b0"], m["se_b0"], m["t0"], m["p0"]),
            (xname, m["b1"], m["se_b1"], m["t1"], m["p1"])]
    est = fmt_fixed([r[1] for r in rows], 4)
    ses = fmt_fixed([r[2] for r in rows], 4)
    tvs = fmt_fixed([r[3] for r in rows], 3)
    cells = [[rows[i][0], est[i], ses[i], tvs[i], pval_coef(rows[i][4]), stars(rows[i][4])]
             for i in range(len(rows))]
    hdr = ["", "Estimate", "Std. Error", "t value", "Pr(>|t|)", ""]
    w = [max(len(hdr[i]), max(len(c[i]) for c in cells)) for i in range(6)]

    out = [
        "", "Call:", f"lm(formula = {formula}, data = {data})", "", "Residuals:",
        format_named(rl, rv), "",
        "Coefficients:",
        hdr[0].ljust(w[0]) + " " + " ".join(hdr[i].rjust(w[i]) for i in range(1, 5)) + "    ",
    ]
    for c in cells:
        out.append(c[0].ljust(w[0]) + " " + " ".join(c[i].rjust(w[i]) for i in range(1, 5))
                   + " " + c[5])
    out += [
        SIGNIF_CODES, "",
        f"Residual standard error: {sig(m['s'], 4)} on {m['df']} degrees of freedom",
        f"Multiple R-squared:  {sig(m['r2'], 4)},\tAdjusted R-squared:  {sig(m['adj_r2'], 4)} ",
        f"F-statistic: {sig(m['f'], 4)} on 1 and {m['df']} DF,  p-value: {pval(m['pf'], 4)}",
        "",
    ]
    return "\n".join(out)


def confint_lm(m, level=0.95, xname="x") -> str:
    crit = qt(1 - (1 - level) / 2, m["df"])
    lo_p, hi_p = (1 - level) / 2 * 100, (1 - (1 - level) / 2) * 100
    rows = [("(Intercept)", m["b0"], m["se_b0"]), (xname, m["b1"], m["se_b1"])]
    los = fmt_common([b - crit * se for _, b, se in rows], 7)
    his = fmt_common([b + crit * se for _, b, se in rows], 7)
    cells = [[rows[i][0], los[i], his[i]] for i in range(len(rows))]
    hdr = ["", f"{sig(lo_p,3)} %", f"{sig(hi_p,3)} %"]
    w = [max(len(hdr[i]), max(len(c[i]) for c in cells)) for i in range(3)]
    out = [hdr[0].ljust(w[0]) + " " + " ".join(hdr[i].rjust(w[i]) for i in (1, 2))]
    for c in cells:
        out.append(c[0].ljust(w[0]) + " " + " ".join(c[i].rjust(w[i]) for i in (1, 2)))
    return "\n".join(out)


def predict_lm(m, x0, level=0.95, interval="confidence"):
    """Point estimate plus a CONFIDENCE or PREDICTION interval at x = x0.

    confidence -> range for the MEAN y of everyone at x0
    prediction -> range for ONE NEW individual at x0  (always wider: it carries
                  the extra +1 term for that individual's own scatter)
    """
    fit = m["b0"] + m["b1"] * x0
    lev = 1 / m["n"] + (x0 - m["xbar"]) ** 2 / m["sxx"]
    core = lev if interval == "confidence" else 1 + lev
    se = m["s"] * math.sqrt(core)
    crit = qt(1 - (1 - level) / 2, m["df"])
    return fit, fit - crit * se, fit + crit * se, se


def format_predict(m, x0, level=0.95, interval="confidence") -> str:
    fit, lo, hi, _ = predict_lm(m, x0, level, interval)
    names = ["", "fit", "lwr", "upr"]
    vals = ["1"] + fmt_common([fit, lo, hi], 7)
    w = [max(len(a), len(b)) for a, b in zip(names, vals)]
    return (" ".join(names[i].rjust(w[i]) for i in range(4)) + "\n" +
            " ".join(vals[i].rjust(w[i]) for i in range(4)))


def cor(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])
