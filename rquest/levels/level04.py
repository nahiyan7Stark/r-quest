"""LEVEL 4 - The normal distribution and assessing normality.

Covers: pnorm and qnorm, the d/p/q/r pattern taught as ONE transferable rule,
the empirical rule, the IQR/s quick check, QQ plots, and the normal
approximation to the binomial with a continuity correction.
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R
from ._common import num

KEY = "chol"
MU, SIGMA = 100.0, 15.0         # the IQ-style example: tidy, familiar numbers
NB, PB = 200, 0.40              # binomial to approximate


def chol():
    return num(KEY, "CHOL")


def build():
    return Level(
        number=4,
        title="The normal distribution",
        subtitle="pnorm, qnorm, the d/p/q/r rule, and four normality checks",
        goal="You can now get probabilities and percentiles out of any normal "
             "distribution, and judge whether real data is normal enough to use them.",
        steps=[

Say("Last level the values were countable: 0, 1, 2 claims. Now the values are "
    "measurements — height, weight, cholesterol — which can land anywhere on a scale. "
    "That changes the shape of the maths, and one shape dominates everything.", "talk"),

Explain(
    "Why a curve instead of bars",
    "For a discrete variable, P(X = 2) is a real, positive number. For a measurement "
    "it is not: the probability that somebody is EXACTLY 175.000000 cm tall is zero, "
    "because there is always another decimal place.\n\n"
    "So continuous distributions answer range questions instead, and probability "
    "becomes AREA UNDER THE CURVE. Total area is 1, and P(X < 170) is the area to the "
    "left of 170. The famous bell-shaped curve is the NORMAL distribution, pinned "
    "down entirely by two numbers: where its centre is (mu) and how wide it is (sigma).",
    {
        "continuous": "the variable can take any value on a scale, decimals included",
        "density curve": "a curve whose AREA gives probability. Height alone means "
                         "nothing on its own",
        "mu (mean)": "where the peak sits",
        "sigma (sd)": "how spread out the curve is. Bigger sigma, flatter and wider",
    }),

Show("pnorm gives you the area to the LEFT",
     f"A normal distribution with mu = {MU:g} and sigma = {SIGMA:g}. The shaded region "
     f"is everything below 115, and its area is the probability of scoring below 115. "
     "That area is precisely what pnorm() returns.",
     lambda fig: P.normal_curve(fig, MU, SIGMA, shade=(None, 115),
                                title=f"pnorm(115, {MU:g}, {SIGMA:g})",
                                xlabel="score", label="P(X < 115)")),

RDemo("pnorm: from a value to a probability",
      f"pnorm(115, mean = {MU:g}, sd = {SIGMA:g})\n"
      f"1 - pnorm(115, mean = {MU:g}, sd = {SIGMA:g})\n"
      f"pnorm(115, {MU:g}, {SIGMA:g}) - pnorm(85, {MU:g}, {SIGMA:g})",
      lambda: f"[1] {R.sig(R.pnorm(115, MU, SIGMA), 7)}\n"
              f"[1] {R.sig(1 - R.pnorm(115, MU, SIGMA), 7)}\n"
              f"[1] {R.sig(R.pnorm(115, MU, SIGMA) - R.pnorm(85, MU, SIGMA), 7)}",
      "pnorm ALWAYS gives the area to the left — that is the only thing it does. "
      "Everything else is arithmetic on top of it: for the right tail, subtract from "
      "1; for a band in the middle, subtract the smaller left-area from the bigger "
      "one.\n\n"
      "There is no k-1 business here. That was a discrete problem; with a continuous "
      "variable, P(X < 115) and P(X <= 115) are the same number."),

AskText(
    prompt=f"Write the R command for the probability that a score is ABOVE 130, given "
           f"mu = {MU:g} and sigma = {SIGMA:g}.",
    answers=[f"1 - pnorm(130, {MU:g}, {SIGMA:g})",
             f"1-pnorm(130, mean = {MU:g}, sd = {SIGMA:g})",
             f"re:1-pnorm\\(130,(mean=)?100,(sd=)?15\\)",
             f"re:pnorm\\(130,(mean=)?100,(sd=)?15,lower\\.tail=f\\)"],
    placeholder="1 - pnorm(value, mean, sd)",
    hint="pnorm only ever gives you the LEFT-hand area. The whole curve has area 1, "
         "so the right-hand piece is what is left over.",
    success=lambda: f"= {R.sig(1 - R.pnorm(130, MU, SIGMA), 6)}, about "
                    f"{1 - R.pnorm(130, MU, SIGMA):.2%}. (R also accepts "
                    f"pnorm(130, {MU:g}, {SIGMA:g}, lower.tail = FALSE), which does "
                    "the subtraction for you.)",
    diagnoses=[
        (r"^\s*pnorm\s*\(\s*130\s*,\s*100",
         "That is the area BELOW 130 — the wrong side. Subtract it from 1 to get the "
         "area above."),
        (r"qnorm", "qnorm() goes the other direction: you hand it a probability and it "
                   "returns a value. Here you have a value and want a probability, so "
                   "it is pnorm()."),
        (r"pnorm\s*\(\s*130\s*\)\s*$",
         "With no mean and sd supplied, R assumes the STANDARD normal (mu = 0, "
         "sigma = 1), so it thinks 130 is 130 standard deviations out. You must pass "
         f"{MU:g} and {SIGMA:g}."),
        (r"pnorm\s*\(\s*15\s*,|pnorm\s*\(\s*100\s*,",
         "The value you are asking about goes FIRST, then the mean, then the sd."),
    ]),

Explain(
    "One rule for every distribution in R: d, p, q, r",
    "You have now met dbinom, pbinom, dpois, ppois and pnorm. They are not five things "
    "to memorise — they are one naming scheme. Every distribution in R gets four "
    "functions, and the first letter tells you the job:\n\n"
    "    d   exactly this value (discrete) or the height of the curve (continuous)\n"
    "    p   probability of this value OR LESS — the area to the left\n"
    "    q   the reverse of p: you give a probability, it gives the value\n"
    "    r   random — generate fake data from this distribution\n\n"
    "Stick the distribution's short name on the end and you have the function: norm, "
    "binom, pois, t, chisq, f. So qt() is the t-distribution's percentile lookup, and "
    "rnorm() invents normal data. Learn the grid once and you never look up a "
    "function name again.",
    {
        "d": "density / exact probability",
        "p": "cumulative probability, always from the left",
        "q": "quantile — the reverse lookup, probability in, value out",
        "r": "random generation",
    }),

Show("q is p run backwards",
     f"pnorm asks 'what fraction is below 115?'. qnorm asks 'what value has 90% below "
     f"it?'. Same curve, same relationship, opposite direction of travel. Here the 90th "
     f"percentile sits at {R.qnorm(0.90, MU, SIGMA):.2f}.",
     lambda fig: P.normal_curve(fig, MU, SIGMA,
                                shade=(None, R.qnorm(0.90, MU, SIGMA)),
                                title=f"qnorm(0.90, {MU:g}, {SIGMA:g}) = "
                                      f"{R.qnorm(0.90, MU, SIGMA):.2f}",
                                xlabel="score", label="area = 0.90",
                                mark=R.qnorm(0.90, MU, SIGMA))),

RDemo("qnorm: from a probability to a value",
      f"qnorm(0.90, mean = {MU:g}, sd = {SIGMA:g})\nqnorm(0.975)",
      lambda: f"[1] {R.sig(R.qnorm(0.90, MU, SIGMA), 7)}\n"
              f"[1] {R.sig(R.qnorm(0.975), 7)}",
      "The first line answers 'you need to be above what score to be in the top 10%?'.\n\n"
      "The second is one you will meet again and again. With no mean or sd given, R "
      "uses the standard normal, and qnorm(0.975) = 1.959964 — the 1.96 that turns up "
      "in every 95% confidence interval for the rest of this course. It is not magic; "
      "it is just the value with 97.5% of the standard normal below it."),

AskChoice(
    prompt="A professor will award scholarships to the top 5% of a normally "
           "distributed exam. Which command finds the cut-off mark?",
    options=[
        "qnorm(0.95, mean = 68, sd = 12)",
        "pnorm(0.95, mean = 68, sd = 12)",
        "qnorm(0.05, mean = 68, sd = 12)",
        "dnorm(0.95, mean = 68, sd = 12)",
    ],
    correct=0,
    feedback=[
        "Right. You are given a probability and want a mark back, so it is a q "
        "function, and the top 5% starts where 95% is below.",
        "pnorm goes the wrong way — it takes a mark and gives a probability. Feeding "
        "it 0.95 asks 'what fraction of students scored below 0.95 marks?'.",
        "qnorm is correct but 0.05 finds the mark with only 5% BELOW it — the bottom "
        "of the class, not the top.",
        "dnorm gives the HEIGHT of the curve at a point, which is not a probability "
        "and is almost never what you want directly.",
    ],
    success="Given a probability and asked for a value, reach for q."),

Explain(
    "Is my data actually normal? Four checks",
    "Every method in the next six levels leans on normality somewhere, so you need a "
    "way to check it rather than assume it. There are four, and you use them together:\n\n"
    "1. HISTOGRAM — does it look roughly bell-shaped and symmetric?\n"
    "2. EMPIRICAL RULE — about 68% of data within 1 sd of the mean, 95% within 2, "
    "99.7% within 3. Count and compare.\n"
    "3. IQR / s — for a genuinely normal distribution this ratio is about 1.3. "
    "Wildly different suggests otherwise.\n"
    "4. QQ PLOT — the sharpest of the four, and the one worth trusting most.\n\n"
    "None of these is a yes/no verdict. You are asking 'normal ENOUGH?', not 'exactly "
    "normal?' — no real data is ever exactly normal.",
    {
        "empirical rule": "the 68 / 95 / 99.7 percentages that hold for any normal curve",
        "IQR / s": "box width divided by standard deviation. About 1.3 if normal",
    }),

Show("Checks 1 and 2: the histogram and the empirical rule",
     lambda: (lambda p: f"The bars follow the orange normal curve reasonably well, and "
              f"the observed percentages ({p[0]:.0%}, {p[1]:.0%}, {p[2]:.0%}) sit close "
              f"to the 68 / 95 / 99.7 a normal distribution promises. That is two "
              f"checks passed.")(R.empirical_rule(chol())),
     lambda fig: P.empirical_rule_plot(fig, chol(), "cholesterol"), tall=True),

RDemo("Checks 2 and 3 in R",
      "m <- mean(chol$CHOL); s <- sd(chol$CHOL)\n"
      "mean(abs(chol$CHOL - m) <= s)      # should be near 0.68\n"
      "mean(abs(chol$CHOL - m) <= 2 * s)  # should be near 0.95\n\n"
      "IQR(chol$CHOL) / sd(chol$CHOL)     # should be near 1.3",
      lambda: (lambda p, r: f"[1] {R.sig(p[0], 4)}\n[1] {R.sig(p[1], 4)}\n\n"
                            f"[1] {R.sig(r, 4)}")(
          R.empirical_rule(chol()), R.iqr_over_s(chol())),
      lambda: "The comparison inside mean() gives TRUE/FALSE for each person, and R "
              "treats TRUE as 1, so averaging them gives the PROPORTION that are "
              "TRUE. That trick is worth remembering.\n\n"
              f"IQR/s here is {R.iqr_over_s(chol()):.2f} against a target of about "
              "1.30. Treat roughly 1.2 to 1.5 as consistent with normality; a value "
              "near 0.9 suggests heavy tails, and one near 1.9 suggests a flat, "
              "boxy distribution."),

Show("Check 4: the QQ plot",
     "This is the one to trust. Each dot compares a value from your data against the "
     "value a perfect normal distribution would have put in that position. If the data "
     "is normal the dots land on the straight line. Dots that curve away at the ends "
     "mean the tails are the wrong weight; a consistent S-shape means skewness.",
     lambda fig: P.qqplot(fig, chol(), "qqnorm(chol$CHOL)")),

RDemo("Drawing a QQ plot",
      "qqnorm(chol$CHOL)\nqqline(chol$CHOL)",
      "(a plot window opens)",
      "qqnorm() draws the dots and qqline() adds the reference line through the "
      "quartiles. You need both — without the line there is nothing to judge "
      "straightness against, and people are surprisingly bad at eyeballing it.\n\n"
      "Say it out loud as 'do the dots hug the line?'. That is the whole test."),

AskText(
    prompt="Draw the QQ plot for the WEIGHT column, then add its reference line. "
           "Write both commands, one per line.",
    answers=["qqnorm(chol$WEIGHT)\nqqline(chol$WEIGHT)",
             "re:qqnorm\\(chol\\$weight\\)qqline\\(chol\\$weight\\)"],
    placeholder="qqnorm(...)   then   qqline(...)",
    hint="Two separate commands, both pointed at the same column. The second one draws "
         "on top of the first.",
    success="qqnorm() then qqline() on the same column is a two-line habit worth "
            "building — it is the fastest normality check you own.",
    diagnoses=[
        (r"qqplot\s*\(", "qqplot() with two q's and no 'norm' compares two datasets to "
                         "each other. To compare one dataset against the normal "
                         "distribution the function is qqnorm()."),
        (r"qqline[\s\S]*qqnorm", "You have them in the wrong order. qqnorm() has to "
                                 "draw the plot before qqline() can add a line to it."),
        (r"^(?![\s\S]*qqline)[\s\S]*qqnorm", "You drew the dots but not the line. "
                                             "Without qqline() there is nothing to "
                                             "judge straightness against."),
    ]),

Explain(
    "Using the normal curve to answer a binomial question",
    "When n is large, adding up dozens of dbinom terms by hand is miserable. The "
    "binomial's shape is close to normal once n is big enough, so you can answer the "
    "question with pnorm instead, using mu = np and sigma = sqrt(np(1-p)).\n\n"
    "The catch is the CONTINUITY CORRECTION. The binomial lives on whole numbers; the "
    "normal curve is smooth. The bar for '80 successes' really covers 79.5 to 80.5, so "
    "before you use pnorm you stretch your boundary by half a unit — outwards if you "
    "want to INCLUDE the endpoint, inwards if you want to exclude it.\n\n"
    "Rule of thumb for when it is safe: np and n(1-p) should both be at least 5.",
    {
        "continuity correction": "the half-unit adjustment that patches the gap "
                                 "between countable bars and a smooth curve",
        "np, n(1-p)": "expected successes and expected failures. Both above 5 and the "
                      "approximation is trustworthy",
    }),

Show("Why the half matters",
     lambda: (lambda mu, sd: f"The binomial bars for n = {NB}, p = {PB} with the "
              f"matching normal curve (mu = np = {mu:g}, sigma = {sd:.3f}) laid over "
              f"them. To capture 'at most 85' you need the area up to the RIGHT EDGE "
              f"of the bar at 85, which is 85.5 — not 85.")(NB * PB,
              (NB * PB * (1 - PB)) ** 0.5),
     lambda fig: (lambda mu, sd: (
         P.normal_curve(fig, mu, sd, shade=(None, 85.5),
                        title=f"Normal approximation: mu = {mu:g}, sigma = {sd:.3f}",
                        xlabel="number of successes",
                        label="P(X <= 85) with correction", mark=85.5)
     ))(NB * PB, (NB * PB * (1 - PB)) ** 0.5)),

AskChoice(
    prompt=f"With n = {NB} and p = {PB}, you want P(X >= 90) using the normal "
           "approximation. Which boundary do you feed to pnorm?",
    options=[
        "89.5, because 'at least 90' includes the whole bar at 90, which starts at 89.5",
        "90.5, because you always add a half",
        "90, because the correction only matters for small n",
        "89, because 'at least 90' means everything above 89",
    ],
    correct=0,
    feedback=[
        "Exactly. You are keeping the bar at 90, so the boundary moves outwards to its "
        "left edge, 89.5. In R: 1 - pnorm(89.5, 80, sqrt(200*0.4*0.6)).",
        "The half always gets added, but the DIRECTION depends on whether the endpoint "
        "is in or out. Here 90 is included, so you move outwards (down) to 89.5.",
        "The correction matters at every n. It matters relatively less when n is huge, "
        "but it is never 'skip it' — and with n = 200 it shifts the answer noticeably.",
        "89 is a whole unit away, not half. You would be scooping up the whole bar at "
        "89, which 'at least 90' excludes.",
    ],
    success=lambda: (lambda mu, sd:
                     f"= 1 - pnorm(89.5, {mu:g}, {sd:.4f}) = "
                     f"{R.sig(1 - R.pnorm(89.5, mu, sd), 5)}, against an exact "
                     f"binomial answer of {R.sig(1 - R.pbinom(89, NB, PB), 5)}. "
                     "Close enough to be useful.")(
        NB * PB, (NB * PB * (1 - PB)) ** 0.5)),

Recap(bullets=[
    "For continuous variables probability is AREA under a curve, and pnorm() always "
    "returns the area to the LEFT. Right tail = 1 - pnorm; middle band = subtract "
    "one pnorm from another.",
    "d / p / q / r is one rule across every distribution: d = exactly, p = cumulative "
    "from the left, q = the reverse lookup, r = random. qnorm(0.975) = 1.96.",
    "Check normality four ways: histogram shape, the 68/95/99.7 empirical rule, "
    "IQR/s near 1.3, and a QQ plot — qqnorm() plus qqline().",
    "The QQ plot is the sharpest check. Dots hugging the line means normal; curved "
    "ends mean the tails are wrong; an S-shape means skew.",
    "For large n you can answer a binomial question with pnorm using mu = np and "
    "sigma = sqrt(np(1-p)), but shift the boundary by half a unit — outwards to "
    "include the endpoint, inwards to exclude it.",
]),
        ])
