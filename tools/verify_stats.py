"""Check every statistic the game prints against known R output.

The expected strings below were taken from a real R session.  If any of these
stop matching, something in rstats.py or distributions.py has drifted and the
game is teaching numbers that RStudio will not reproduce.

    python tools/verify_stats.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from rquest import datasets as D, rstats as R
from rquest import distributions as dist

fails = []


def eq(name, got, want, tol=None):
    if tol is None:
        ok = str(got).strip() == str(want).strip()
    else:
        ok = abs(float(got) - float(want)) <= tol
    print(("  ok   " if ok else "  FAIL ") + name)
    if not ok:
        fails.append(name)
        print(f"        got  {got!r}\n        want {want!r}")


print("distribution functions (R values)")
eq("qnorm(0.975)", dist.norm_ppf(.975), 1.959963984540054, 1e-12)
eq("qnorm(0.995)", dist.norm_ppf(.995), 2.5758293035489004, 1e-11)
eq("pnorm(1.96)", dist.norm_cdf(1.96), 0.9750021048517796, 1e-13)
eq("qt(0.975, 30)", dist.t_ppf(.975, 30), 2.0422724563012373, 1e-9)
eq("qt(0.975, 9)", dist.t_ppf(.975, 9), 2.2621571627982053, 1e-9)
eq("pt(-4.0621, 9)", dist.t_cdf(-4.0621, 9), 0.00141650392019508, 1e-12)
eq("qchisq(0.95, 2)", dist.chi2_ppf(.95, 2), 5.991464547107979, 1e-9)
eq("pchisq(5, 2)", dist.chi2_cdf(5, 2), 0.9179150013761012, 1e-12)
eq("dbinom(3, 10, 0.3)", dist.binom_pmf(3, 10, .3), 0.26682793199999966, 1e-14)
eq("pbinom(3, 10, 0.3)", dist.binom_cdf(3, 10, .3), 0.6496107184000001, 1e-12)
eq("dpois(2, 4)", dist.pois_pmf(2, 4), 0.14652511110987343, 1e-14)
eq("ppois(2, 4)", dist.pois_cdf(2, 4), 0.238103305553544, 1e-12)

print("\nsummary(mtcars$mpg)")
m = D.load("mtcars", force_offline=True).df
eq("summary", R.summary(m.mpg),
   "   Min. 1st Qu.  Median    Mean 3rd Qu.    Max. \n"
   "  10.40   15.43   19.20   20.09   22.80   33.90 ")
eq("sd(mtcars$wt)", R.sd(m.wt), 0.9784574, 1e-7)
eq("var(mtcars$mpg)", R.var(m.mpg), 36.3241, 1e-4)

print("\nt.test(len ~ supp, data = ToothGrowth)  [Welch]")
t = D.load("tooth", force_offline=True).df
oj = np.asarray(t[t.supp == "OJ"].len, float)
vc = np.asarray(t[t.supp == "VC"].len, float)
w = R.t_test(oj, vc, data_line="len by supp", group_names=("OJ", "VC"))
eq("t", w["t"], 1.91526826869, 1e-9)
eq("df", w["df"], 55.3094327, 1e-6)   # R prints 55.309
eq("p", w["p"], 0.06063451, 1e-8)
eq("CI lower", w["conf_int"][0], -0.1710156, 1e-6)
eq("CI upper", w["conf_int"][1], 7.5710156, 1e-6)

print("\nt.test(..., var.equal = TRUE)  [pooled]")
po = R.t_test(oj, vc, var_equal=True)
eq("df", po["df"], 58, 0)
eq("p", po["p"], 0.06039, 1e-5)

print("\nt.test(extra ~ group, data = sleep, paired = TRUE)")
s = D.load("sleep", force_offline=True).df
a = np.asarray(s[s.group == 1].extra, float)
b = np.asarray(s[s.group == 2].extra, float)
pr = R.t_test(a, b, paired=True)
eq("t", pr["t"], -4.062128, 1e-6)
eq("df", pr["df"], 9, 0)
eq("p", pr["p"], 0.002833, 1e-6)
eq("CI lower", pr["conf_int"][0], -2.4598858, 1e-6)

print("\nsummary(lm(mpg ~ wt, data = mtcars))")
f = R.lm(m.wt, m.mpg)
eq("intercept", f["b0"], 37.285126, 1e-5)
eq("slope", f["b1"], -5.344472, 1e-6)
eq("se slope", f["se_b1"], 0.5591010, 1e-7)
eq("R-squared", f["r2"], 0.7528328, 1e-7)
eq("residual se", f["s"], 3.045882, 1e-6)
eq("F", f["f"], 91.37533, 1e-5)
eq("coefficient table row", R.format_lm_summary(f, "mpg ~ wt", "mtcars", "wt")
   .splitlines()[11], "wt           -5.3445     0.5591  -9.559 1.29e-10 ***")

print("\nconfint / predict at wt = 3")
eq("confint slope lo", f["b1"] - R.qt(.975, f["df"]) * f["se_b1"], -6.486308, 1e-6)
eq("confint slope hi", f["b1"] + R.qt(.975, f["df"]) * f["se_b1"], -4.202635, 1e-6)
c = R.predict_lm(f, 3, interval="confidence")
p = R.predict_lm(f, 3, interval="prediction")
eq("fit", c[0], 21.25171, 1e-5)
eq("conf lwr", c[1], 20.12444, 1e-5)
eq("conf upr", c[2], 22.37899, 1e-5)
eq("pred lwr", p[1], 14.92987, 1e-5)
eq("pred upr", p[2], 27.57355, 1e-5)
if not (p[2] - p[1] > c[2] - c[1]):
    fails.append("prediction interval is not wider than the confidence interval")

print("\nchisq.test")
g = R.chisq_gof([30, 40, 50])
eq("X-squared", g["chi"], 5, 1e-12)
eq("df", g["df"], 2, 0)
eq("p", g["p"], 0.08208500, 1e-8)

print("\nprop.test(29, 300, p = 0.05)")
pt = R.prop_test(29, 300, p=0.05)
eq("X-squared", pt["chi"], 12.78947, 1e-5)

print("\nt.test on the boss dataset (iris, versicolor vs virginica)")
d = D.load("iris", force_offline=True).df
ve = np.asarray(d[d.Species == "versicolor"]["Sepal.Width"], float)
vi = np.asarray(d[d.Species == "virginica"]["Sepal.Width"], float)
bt = R.t_test(ve, vi)
eq("t", bt["t"], -3.205761, 1e-6)
eq("df", bt["df"], 97.9268267, 1e-6)  # R prints 97.927
eq("p", bt["p"], 0.001819, 1e-6)

print()
if fails:
    print(f"{len(fails)} MISMATCH(ES) against R:")
    for f_ in fails:
        print("  -", f_)
    sys.exit(1)
print("every printed statistic matches R")
