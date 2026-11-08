"""LEVEL 6 - Confidence intervals.

Covers: the large-sample z interval for a mean, the small-sample t interval
via t.test()$conf.int, the proportion interval via prop.test(), and an honest
answer to why a 90% interval is narrower than a 95% one.
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R
from ._common import num, frame

KEY = "chol"
SMALL_N = 12


def chol():
    return num(KEY, "CHOL")


def small():
    """A deliberately small sample, so t and z genuinely differ."""
    rng = np.random.default_rng(7)
    return chol()[rng.choice(len(chol()), SMALL_N, replace=False)]


def dead_counts():
    m = frame(KEY)["MORT"]
    return int((m == "dead").sum()), len(m)


def build():
    return Level(
        number=6,
        title="Confidence intervals",
        subtitle="z, t and proportion intervals, and what the % actually means",
        goal="You can now build an interval estimate for a mean or a proportion and "
             "say what the confidence level does and does not promise.",
        steps=[

Say("Level 5 said x-bar jumps around from sample to sample. So reporting a single "
    "number and stopping is a bit dishonest. This level is about reporting a RANGE "
    "with a stated level of confidence instead.", "talk"),

Explain(
    "Point estimate versus interval estimate",
    "Your sample mean is a POINT ESTIMATE: one number, your best single guess at mu. "
    "It is also almost certainly a little bit wrong, and it does not admit that.\n\n"
    "A CONFIDENCE INTERVAL is a range built to have a stated chance of containing the "
    "real mu. It is always 'estimate, plus or minus a margin', and the margin is built "
    "from two things you already know: the standard error from Level 5, and a "
    "multiplier from Level 4's qnorm.\n\n"
    "    interval  =  x-bar  ±  (multiplier × standard error)",
    {
        "point estimate": "a single best guess, like x-bar",
        "interval estimate": "a range of plausible values with a confidence level attached",
        "margin of error": "the ± part: multiplier times standard error",
        "confidence level": "how often this PROCEDURE captures the truth, over many "
                            "repeated samples",
    }),

Show("What '95% confident' actually means",
     "A hundred samples, a hundred intervals, all from the same population. Each is "
     "different because each sample was different. About 95 of them contain the true "
     "mean (the dashed line) and about five, drawn in red, miss it entirely.\n\n"
     "The confidence level is a property of the METHOD across many samples, not a "
     "probability about the one interval you happen to have. Your interval either "
     "contains mu or it does not — you just cannot tell which.",
     lambda fig: _coverage(fig), tall=True),

RDemo("A large-sample z interval for the mean",
      "n <- length(chol$CHOL)\n"
      "xbar <- mean(chol$CHOL)\n"
      "se <- sd(chol$CHOL) / sqrt(n)\n"
      "zstar <- qnorm(0.975)          # 1.959964\n\n"
      "c(xbar - zstar * se, xbar + zstar * se)",
      lambda: (lambda lo, hi, z, se, n, xb:
               f"[1] {R.sig(lo, 7)} {R.sig(hi, 7)}\n\n"
               f"# n = {n},  xbar = {R.sig(xb, 6)},  se = {R.sig(se, 5)}")(
          *R.z_interval(chol())),
      lambda: (lambda lo, hi, z, se, n, xb:
               f"Four lines, each one a thing you already know. qnorm(0.975) gives "
               f"1.96 because a 95% interval leaves 2.5% in EACH tail — that is where "
               f"the 0.975 comes from, and it is the step people get wrong.\n\n"
               f"With n = {n} this is a large sample, so the CLT from Level 5 "
               "guarantees x-bar is normal and the z multiplier is safe.")(
          *R.z_interval(chol()))),

AskChoice(
    prompt="For a 99% confidence interval, what goes inside qnorm()?",
    options=["0.995", "0.99", "0.01", "0.495"],
    correct=0,
    feedback=[
        "Right. 99% in the middle leaves 1% split between two tails, so 0.5% in each, "
        "so 99.5% sits below the upper multiplier. qnorm(0.995) = 2.576.",
        "0.99 leaves 1% in ONE tail only. That is the multiplier for a one-sided "
        "situation, and using it here would give you a 98% two-sided interval.",
        "0.01 finds the value with only 1% BELOW it, which is the negative multiplier "
        "at the bottom end. You would get -2.326.",
        "Halving the confidence level is not the move. The rule is 1 - (1 - level)/2, "
        "which for 99% gives 0.995.",
    ],
    success="The recipe is always qnorm(1 - (1 - level)/2): 0.95 gives 0.975, "
            "0.99 gives 0.995, 0.90 gives 0.95."),

Explain(
    "Small samples need the t distribution",
    "The z interval quietly assumed you knew sigma. You do not — you used s from your "
    "sample instead. With 300 people that swap barely matters. With 12 it matters a "
    "lot, because s is itself a shaky estimate, and pretending otherwise makes your "
    "interval too narrow.\n\n"
    "The t distribution fixes this. It looks like the normal curve but with fatter "
    "tails, so it hands you a bigger multiplier. How much bigger depends on the "
    "DEGREES OF FREEDOM, which here is n - 1. As n grows, t quietly turns back into z.",
    {
        "t distribution": "a bell curve with heavier tails, used when sigma is estimated",
        "degrees of freedom (df)": "n - 1 for a one-sample problem. Roughly, how much "
                                   "independent information you have left after "
                                   "estimating the mean",
        "qt(0.975, df)": "the t version of qnorm(0.975)",
    }),

Show("t is a normal curve that does not trust you yet",
     lambda: f"With {SMALL_N - 1} degrees of freedom the t multiplier is "
             f"{R.qt(0.975, SMALL_N - 1):.3f} against z's 1.960 — about "
             f"{100*(R.qt(0.975, SMALL_N-1)/1.959964 - 1):.0f}% wider. By df = 100 the "
             "two are practically identical, which is why 'large sample' means you can "
             "stop worrying about the difference.",
     lambda fig: _t_vs_z(fig)),

RDemo("The easy way: t.test() already computes the interval",
      "small <- chol$CHOL[1:12]\nt.test(small)",
      lambda: R.t_test(small(), data_line="small")["text"],
      lambda: (lambda r:
               "t.test() is really a hypothesis test — that is next level — but it "
               "prints the confidence interval for free, and this is how the labs get "
               "one. To pull out just the two numbers:\n\n"
               "    t.test(small)$conf.int\n\n"
               "and for a different level:\n\n"
               "    t.test(small, conf.level = 0.99)$conf.int\n\n"
               f"Notice how much wider this is than the z interval on all 300 people. "
               "Twelve observations buy you very little precision.")(
          R.t_test(small()))),

AskText(
    prompt="Write the command that gives a 90% confidence interval for the mean of a "
           "vector called small, and nothing else.",
    answers=["t.test(small, conf.level = 0.90)$conf.int",
             "re:t\\.test\\(small,conf\\.level=0\\.90?\\)\\$conf\\.int"],
    placeholder="t.test(x, conf.level = ...)$conf.int",
    hint="Two additions to a plain t.test(small): the argument that sets the level, "
         "and the $ that pulls one piece out of the result.",
    success=lambda: (lambda r: f"Which gives {R.sig(r['conf_int'][0], 6)} to "
                     f"{R.sig(r['conf_int'][1], 6)} — narrower than the 95% interval, "
                     "for reasons we are about to make explicit.")(
        R.t_test(small(), conf=0.90)),
    diagnoses=[
        (r"conf\.level\s*=\s*(90|10)\b",
         "conf.level takes a PROPORTION, not a percentage. 90% is 0.90; writing 90 "
         "makes R complain that the level must be between 0 and 1."),
        (r"conf\.level\s*=\s*0?\.10\b",
         "0.10 asks for a 10% confidence interval — a tiny sliver around the mean. "
         "You want 0.90."),
        (r"t\.test\s*\(\s*small\s*\)\s*$",
         "That gives the default 95% interval, and prints the whole test as well. "
         "You need conf.level = 0.90 and $conf.int on the end."),
        (r"z\.test|qnorm",
         "With a small sample and sigma unknown, the multiplier has to come from the "
         "t distribution. t.test() handles that for you."),
        (r"\$conf\b(?!\.int)",
         "The piece is called conf.int, with the .int on the end."),
    ]),

Explain(
    "Confidence intervals for a proportion",
    "Sometimes the thing you are estimating is not an average but a PERCENTAGE: the "
    "share of patients who died, the share of voters who approve. The logic is "
    "identical — estimate plus or minus a margin — but the standard error formula "
    "changes, because for a proportion the spread is determined by the proportion "
    "itself.\n\n"
    "R's prop.test() does the whole thing. You give it two numbers: how many "
    "successes, and how many trials.",
    {
        "proportion": "a count divided by a total, always between 0 and 1",
        "p-hat": "the sample proportion — your point estimate of the true p",
        "successes / trials": "the two numbers prop.test needs, in that order",
    }),

RDemo("prop.test for one proportion",
      lambda: (lambda k, n: f"# {k} of the {n} people in the study had died\n"
                            f"prop.test({k}, {n})")(*dead_counts()),
      lambda: (lambda k, n: R.prop_test(k, n, p=0.5)["text"])(*dead_counts()),
      lambda: (lambda k, n, r:
               f"Ignore the test part for now — the line you want is the confidence "
               f"interval: {R.sig(r['conf_int'][0], 4)} to "
               f"{R.sig(r['conf_int'][1], 4)}. So roughly "
               f"{100*r['conf_int'][0]:.1f}% to {100*r['conf_int'][1]:.1f}% of the "
               f"wider population this sample came from.\n\n"
               f"The point estimate {k}/{n} = {k/n:.4f} sits inside it, though not "
               "always exactly in the middle — proportion intervals are slightly "
               "lopsided when p-hat is far from 0.5.")(
          *dead_counts(), R.prop_test(dead_counts()[0], dead_counts()[1], p=0.5))),

AskText(
    prompt="In a survey, 145 of 400 students said they commute by bus. Write the "
           "command that gives a confidence interval for the true proportion.",
    answers=["prop.test(145, 400)", "re:prop\\.test\\(145,400(,.*)?\\)",
             "prop.test(x = 145, n = 400)"],
    placeholder="prop.test(successes, trials)",
    hint="Two numbers, successes first and the total second. Do not divide them "
         "yourself — R wants the raw counts.",
    success=lambda: (lambda r: f"The interval comes out as "
                     f"{R.sig(r['conf_int'][0], 4)} to {R.sig(r['conf_int'][1], 4)}, "
                     f"around the point estimate of {145/400:.4f}.")(
        R.prop_test(145, 400, p=0.5)),
    diagnoses=[
        (r"prop\.test\s*\(\s*0?\.3625",
         "You divided first. prop.test() wants the two COUNTS — it needs to know the "
         "sample size to work out the standard error, and 0.3625 alone hides that."),
        (r"prop\.test\s*\(\s*400\s*,\s*145",
         "Wrong way round. Successes come first, then the total: prop.test(145, 400)."),
        (r"t\.test|z\.test",
         "Those are for MEANS of numeric data. Bus-or-not is a yes/no outcome, so the "
         "summary is a proportion and the function is prop.test()."),
        (r"prop\.test\s*\(\s*145\s*\)",
         "145 on its own does not say out of how many. prop.test needs both numbers."),
    ]),

Show("Why a 90% interval is narrower than a 95%",
     "Same sample, same standard error, three confidence levels. The only thing that "
     "changes is the multiplier: 1.645, then 1.960, then 2.576.\n\n"
     "So the width is bought with confidence. A wider net catches the true value more "
     "often, and a narrower one is more useful but wrong more often. There is no "
     "setting that gives you both, which is exactly why you have to state the level "
     "whenever you report an interval.",
     lambda fig: (lambda z: P.ci_width_compare(fig, float(chol().mean()), z[3]))(
         R.z_interval(chol()))),

AskChoice(
    prompt="Your 95% CI for mean cholesterol is 236 to 249. A classmate says 'so there "
           "is a 95% chance mu is between 236 and 249'. What is wrong with that?",
    options=[
        "mu is a fixed number, so it is either in that range or it is not. The 95% "
        "describes how often intervals built this way capture mu, not this one interval",
        "Nothing — that is exactly what a confidence interval means",
        "The interval should have been 90% instead",
        "Nothing is wrong with the logic, but the numbers should be rounded",
    ],
    correct=0,
    feedback=[
        "Exactly. It is a statement about the PROCEDURE over many samples. Once you "
        "have a specific interval, the coin has already been flipped — you just do "
        "not get to see the result.",
        "It is the most common misreading in the whole course, and it is worth marks "
        "on an exam. mu does not have a probability distribution; it is a fixed "
        "constant we do not happen to know.",
        "The level is your choice and 95% is a perfectly normal one. The problem is "
        "with the interpretation, not the number.",
        "Rounding is not the issue. The problem is treating mu as random when it is "
        "the interval that is random.",
    ],
    success="Say it as: 'we are 95% confident that the interval contains mu' — "
            "confidence in the method, not probability about mu."),

Recap(bullets=[
    "A confidence interval is estimate ± (multiplier × standard error). The standard "
    "error comes from Level 5; the multiplier comes from qnorm or qt.",
    "Large sample: use z, with qnorm(1 - (1 - level)/2) — 1.96 for 95%. Small sample "
    "with sigma unknown: use t, and let t.test(x)$conf.int do the work.",
    "For a proportion, prop.test(successes, trials) gives the interval. Pass the raw "
    "counts, never the proportion you worked out yourself.",
    "Higher confidence means a bigger multiplier means a wider interval. 90% is "
    "narrower than 95% because it is willing to be wrong more often.",
    "The level describes the procedure across many samples. Never say 'there is a 95% "
    "chance mu is in here' about one specific interval.",
]),
        ])


def _coverage(fig):
    """100 intervals from the same population; the misses drawn in red."""
    rng = np.random.default_rng(11)
    x = chol()
    mu = float(x.mean())
    rows = []
    for _ in range(100):
        s = x[rng.choice(len(x), 40, replace=False)]
        lo, hi, z, se, n, xb = R.z_interval(s)
        rows.append((lo, hi, xb, lo <= mu <= hi))
    hits = sum(1 for r in rows if r[3])
    P.ci_ladder(fig, rows, truth=mu,
                title=f"100 separate 95% intervals - {hits} of them contain the truth",
                xlabel="cholesterol (mg/dL)")


def _t_vs_z(fig):
    from .. import theme as T
    from .. import distributions as D
    ax = P.new_axes(fig, "t with 11 df against the standard normal",
                    "value", "density")
    xs = np.linspace(-4.5, 4.5, 500)
    ax.plot(xs, [D.norm_pdf(v) for v in xs], color=T.SERIES[0], lw=2.2,
            label="normal (z)")
    ax.plot(xs, [D.t_pdf(v, SMALL_N - 1) for v in xs], color=T.WARN, lw=2.2,
            label=f"t, df = {SMALL_N - 1}")
    for v, col, lab in ((1.959964, T.SERIES[0], "z* = 1.960"),
                        (R.qt(0.975, SMALL_N - 1), T.WARN,
                         f"t* = {R.qt(0.975, SMALL_N - 1):.3f}")):
        ax.axvline(v, color=col, ls=":", lw=1.5)
        ax.text(v, 0.30, "  " + lab, color=col, fontsize=9)
    ax.legend(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID, labelcolor=T.INK, fontsize=9)
    ax.set_ylim(bottom=0)
