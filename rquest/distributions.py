"""Probability distributions in pure Python -- no SciPy required.

The game must install with nothing but pandas and matplotlib so that a
classmate can get it running in one pip command.  That means the normal, t,
chi-square, F, binomial and Poisson distributions all have to be implemented
here, and they have to be accurate enough that the numbers on screen match
what R prints to seven significant figures.

Everything below is standard numerical-analysis material:
  * qnorm  -- Wichura's AS 241 algorithm (accurate to ~16 digits)
  * pt, pf -- regularised incomplete beta via a Lentz continued fraction
  * pchisq -- regularised incomplete gamma via series / continued fraction
  * ppf's  -- safeguarded bisection on the matching cdf
Each function is checked against known R output in tools/verify_stats.py.
"""

from __future__ import annotations

import math

SQRT2 = math.sqrt(2.0)
SQRT2PI = math.sqrt(2.0 * math.pi)
_EPS = 3.0e-16
_TINY = 1.0e-300


# ==========================================================================
# Normal
# ==========================================================================

def norm_pdf(x, mean=0.0, sd=1.0):
    z = (x - mean) / sd
    return math.exp(-0.5 * z * z) / (sd * SQRT2PI)


def norm_cdf(x, mean=0.0, sd=1.0):
    return 0.5 * math.erfc(-((x - mean) / sd) / SQRT2)


def norm_ppf(p, mean=0.0, sd=1.0):
    """Inverse normal CDF -- Wichura (1988), algorithm AS 241."""
    if p <= 0.0:
        return float("-inf")
    if p >= 1.0:
        return float("inf")
    q = p - 0.5
    if abs(q) <= 0.425:
        r = 0.180625 - q * q
        num = (((((((2509.0809287301226727 * r + 33430.575583588128105) * r +
                    67265.770927008700853) * r + 45921.953931549871457) * r +
                  13731.693765509461125) * r + 1971.5909503065514427) * r +
                133.14166789178437745) * r + 3.387132872796366608)
        den = (((((((5226.495278852854561 * r + 28729.085735721942674) * r +
                    39307.89580009271061) * r + 21213.794301586595867) * r +
                  5394.1960214247511077) * r + 687.1870074920579083) * r +
                42.313330701600911252) * r + 1.0)
        return mean + sd * q * num / den
    r = p if q < 0 else 1.0 - p
    r = math.sqrt(-math.log(r))
    if r <= 5.0:
        r -= 1.6
        num = (((((((7.7454501427834140764e-4 * r + 0.0227238449892691845833) * r +
                    0.24178072517745061177) * r + 1.27045825245236838258) * r +
                  3.64784832476320460504) * r + 5.7694972214606914055) * r +
                4.6303378461565452959) * r + 1.42343711074968357734)
        den = (((((((1.05075007164441684324e-9 * r + 5.475938084995344946e-4) * r +
                    0.0151986665636164571966) * r + 0.14810397642748007459) * r +
                  0.68976733498510000455) * r + 1.6763848301838038494) * r +
                2.05319162663775882187) * r + 1.0)
    else:
        r -= 5.0
        num = (((((((2.01033439929228813265e-7 * r + 2.71155556874348757815e-5) * r +
                    0.0012426609473880784386) * r + 0.026532189526576123093) * r +
                  0.29656057182850489123) * r + 1.7848265399172913358) * r +
                5.4637849111641143699) * r + 6.6579046435011037772)
        den = (((((((2.04426310338993978564e-15 * r + 1.4215117583164458887e-7) * r +
                    1.8463183175100546818e-5) * r + 7.868691311456132591e-4) * r +
                  0.0148753612908506148525) * r + 0.13692988092273580531) * r +
                0.59983220655588793769) * r + 1.0)
    val = num / den
    if q < 0:
        val = -val
    return mean + sd * val


# ==========================================================================
# Log-gamma helpers and the two incomplete special functions
# ==========================================================================

def lbeta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta (modified Lentz method)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < _TINY:
        d = _TINY
    d = 1.0 / d
    h = d
    for m in range(1, 301):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < _TINY:
            d = _TINY
        c = 1.0 + aa / c
        if abs(c) < _TINY:
            c = _TINY
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < _TINY:
            d = _TINY
        c = 1.0 + aa / c
        if abs(c) < _TINY:
            c = _TINY
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(a * math.log(x) + b * math.log1p(-x) - lbeta(a, b))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - math.exp(b * math.log1p(-x) + a * math.log(x) - lbeta(b, a)) \
        * _betacf(b, a, 1.0 - x) / b


def _gamma_series(s, x):
    ap, total, delta = s, 1.0 / s, 1.0 / s
    for _ in range(1000):
        ap += 1.0
        delta *= x / ap
        total += delta
        if abs(delta) < abs(total) * _EPS:
            break
    return total * math.exp(-x + s * math.log(x) - math.lgamma(s))


def _gamma_cf(s, x):
    b = x + 1.0 - s
    c = 1.0 / _TINY
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - s)
        b += 2.0
        d = an * d + b
        if abs(d) < _TINY:
            d = _TINY
        c = b + an / c
        if abs(c) < _TINY:
            c = _TINY
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            break
    return math.exp(-x + s * math.log(x) - math.lgamma(s)) * h


def gammainc(s, x):
    """Regularised lower incomplete gamma P(s, x)."""
    if x <= 0.0:
        return 0.0
    if x < s + 1.0:
        return _gamma_series(s, x)
    return 1.0 - _gamma_cf(s, x)


# ==========================================================================
# Student's t
# ==========================================================================

def t_pdf(x, df):
    return math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) \
        / math.sqrt(df * math.pi) * (1 + x * x / df) ** (-(df + 1) / 2)


def t_cdf(t, df):
    x = df / (df + t * t)
    half = 0.5 * betainc(df / 2.0, 0.5, x)
    return half if t <= 0 else 1.0 - half


def _bisect(fn, target, lo, hi, tol=1e-12, iters=200):
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if fn(mid) < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol * max(1.0, abs(mid)):
            break
    return 0.5 * (lo + hi)


def t_ppf(p, df):
    if p <= 0:
        return float("-inf")
    if p >= 1:
        return float("inf")
    guess = abs(norm_ppf(p))
    hi = max(guess * 4.0 + 10.0, 50.0)
    return _bisect(lambda v: t_cdf(v, df), p, -hi, hi)


# ==========================================================================
# Chi-square and F
# ==========================================================================

def chi2_pdf(x, df):
    if x <= 0:
        return 0.0
    k = df / 2.0
    return math.exp((k - 1) * math.log(x) - x / 2.0 - k * math.log(2.0) - math.lgamma(k))


def chi2_cdf(x, df):
    return gammainc(df / 2.0, x / 2.0) if x > 0 else 0.0


def chi2_ppf(p, df):
    if p <= 0:
        return 0.0
    if p >= 1:
        return float("inf")
    hi = max(df * 10.0 + 50.0, 10.0)
    while chi2_cdf(hi, df) < p:
        hi *= 2.0
    return _bisect(lambda v: chi2_cdf(v, df), p, 0.0, hi)


def f_cdf(x, d1, d2):
    if x <= 0:
        return 0.0
    return betainc(d1 / 2.0, d2 / 2.0, d1 * x / (d1 * x + d2))


# ==========================================================================
# Binomial and Poisson
# ==========================================================================

def _lchoose(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def binom_pmf(k, n, p):
    k = int(round(k))
    if k < 0 or k > n:
        return 0.0
    if p <= 0.0:
        return 1.0 if k == 0 else 0.0
    if p >= 1.0:
        return 1.0 if k == n else 0.0
    return math.exp(_lchoose(n, k) + k * math.log(p) + (n - k) * math.log1p(-p))


def binom_cdf(k, n, p):
    k = math.floor(k)
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    # regularised incomplete beta is exact and avoids summing thousands of terms
    return betainc(n - k, k + 1, 1.0 - p)


def pois_pmf(k, lam):
    k = int(round(k))
    if k < 0:
        return 0.0
    if lam == 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))


def pois_cdf(k, lam):
    k = math.floor(k)
    if k < 0:
        return 0.0
    return 1.0 - gammainc(k + 1.0, lam)


# ==========================================================================
# Small helpers the tests and plots need
# ==========================================================================

def ppoints(n):
    """R's ppoints(): the plotting positions qqnorm() uses."""
    a = 3.0 / 8.0 if n <= 10 else 0.5
    return [(i + 1 - a) / (n + 1 - 2 * a) for i in range(n)]


def qq_theoretical(n):
    """Theoretical normal quantiles for a sample of size n, R's qqnorm order."""
    return [norm_ppf(p) for p in ppoints(n)]
