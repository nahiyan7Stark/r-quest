"""LEVEL 5 - Sampling distributions and the Central Limit Theorem.

Covers: the difference between a population, a sample and a sampling
distribution; simulating many samples with a for loop and storing the means;
seeing the CLT happen; and QQ-checking the simulated means.
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R

SEED = 2500
NPOP = 20000
NSAMP = 1000        # how many samples we draw
N = 30              # size of each sample

_cache = {}


def population():
    """A deliberately LOPSIDED population, so the CLT has something to prove."""
    if "pop" not in _cache:
        rng = np.random.default_rng(SEED)
        # waiting times: heavily right-skewed, nothing like a bell curve
        _cache["pop"] = rng.exponential(scale=8.0, size=NPOP) + 1.0
    return _cache["pop"]


def sample_means(n=N, reps=NSAMP):
    key = f"sm{n}_{reps}"
    if key not in _cache:
        rng = np.random.default_rng(SEED + n)
        pop = population()
        idx = rng.integers(0, len(pop), size=(reps, n))
        _cache[key] = pop[idx].mean(axis=1)
    return _cache[key]


def pop_mu():
    return float(population().mean())


def pop_sigma():
    return R.sd(population())


def build():
    return Level(
        number=5,
        title="Sampling & the CLT",
        subtitle="Why sample means behave better than the data they came from",
        goal="You can now explain what a sampling distribution is, predict its "
             "spread with sigma/sqrt(n), and say why the normal curve keeps turning "
             "up even when the data is not normal.",
        steps=[

Say("You just spent a level learning to check whether data is normal. Fair question: "
    "what do we do when it plainly is not? This level is the answer, and it is the "
    "hinge the whole second half of the course swings on.", "think"),

Explain(
    "Three different things that all get called 'the mean'",
    "Keeping these apart is the single most important idea in the course.\n\n"
    "The POPULATION is everyone you care about — all customers, all patients. Its mean "
    "is a fixed number you will almost never know. We call it mu.\n\n"
    "A SAMPLE is the handful you actually measured. Its mean, x-bar, you can compute — "
    "and if you took a different sample you would get a different x-bar.\n\n"
    "That last sentence is the important one. x-bar is itself a random variable, and "
    "the distribution of all the x-bars you could have got is called the SAMPLING "
    "DISTRIBUTION OF THE MEAN. It is a distribution of averages, not of people.",
    {
        "population": "everyone you care about. Its mean mu is fixed and usually unknown",
        "sample": "the subset you measured. Its mean x-bar changes from sample to sample",
        "sampling distribution": "the distribution of x-bar over all the samples you "
                                 "could have taken",
        "parameter vs statistic": "mu is a parameter (about the population); x-bar is "
                                  "a statistic (about your sample)",
    }),

Show("A population that is nowhere near normal",
     lambda: f"Customer waiting times for 20,000 people: a hard floor at zero, a big "
             f"pile of short waits and a long tail of unlucky ones. Mean "
             f"{pop_mu():.2f} minutes, sd {pop_sigma():.2f}. No amount of squinting "
             "turns that into a bell curve.",
     lambda fig: P.histogram(fig, population(), bins=45,
                             title="The population: waiting times",
                             xlabel="minutes", show_normal=True)),

Explain(
    "The experiment we are about to run",
    "Take a sample of 30 people, write down the mean. Put them back, take another 30, "
    "write down that mean. Do it a thousand times, then draw a histogram of the "
    "thousand means.\n\n"
    "In real life you never do this — you get one sample and that is it. We can do it "
    "here because we are pretending to know the whole population, which lets us watch "
    "the machinery that is normally hidden.",
    {
        "replication": "repeating the whole sampling process many times",
        "x-bar": "the mean of one sample. Each repetition produces one new x-bar",
    }),

RDemo("Simulating it with a for loop",
      'set.seed(2500)\n'
      'means <- numeric(1000)          # an empty box with 1000 slots\n\n'
      'for (i in 1:1000) {\n'
      '  s <- sample(population, size = 30, replace = TRUE)\n'
      '  means[i] <- mean(s)\n'
      '}\n\n'
      'mean(means)\nsd(means)',
      lambda: f"[1] {R.sig(float(sample_means().mean()), 6)}\n"
              f"[1] {R.sig(R.sd(sample_means()), 6)}",
      lambda:
      "Read the loop in English: 'for each i from 1 to 1000, draw a sample of 30, "
      "take its mean, and put that mean in slot i'. numeric(1000) makes the empty "
      "box first, because R likes to know how big the box will be.\n\n"
      f"set.seed() fixes the random number generator so you get the same answer twice "
      f"— essential when you are marking your own work.\n\n"
      f"Look at those two numbers against the population's mu = {pop_mu():.2f} and "
      f"sigma = {pop_sigma():.2f}. The average of the means landed on mu. The SPREAD "
      f"did not: it shrank."),

Explain(
    "The Central Limit Theorem",
    "Here is what the simulation is about to show, stated properly. For a sample of "
    "size n drawn from a population with mean mu and standard deviation sigma:\n\n"
    "  • the sampling distribution of x-bar is centred on mu\n"
    "  • its standard deviation is sigma / sqrt(n), called the STANDARD ERROR\n"
    "  • and as n grows, its shape becomes normal — WHATEVER the population looked like\n\n"
    "That third point is the miracle. It means every normal-based method you are about "
    "to learn works on skewed, lumpy, ugly real data, provided your sample is big "
    "enough. The usual rule of thumb is n of 30 or more.",
    {
        "standard error": "the standard deviation of a statistic. For the sample mean "
                          "it is sigma/sqrt(n)",
        "sqrt(n)": "the square root of the sample size — why quadrupling your sample "
                   "only halves your error",
    }),

Show("The Central Limit Theorem, actually happening",
     lambda: f"Left: the population, violently skewed. Right: a thousand means of "
             f"samples of {N}, with a normal curve drawn over them. Same underlying "
             f"data. The skew is gone, and the spread has collapsed from "
             f"{pop_sigma():.2f} down to {R.sd(sample_means()):.2f} — almost exactly "
             f"{pop_sigma():.2f}/sqrt({N}) = {pop_sigma()/np.sqrt(N):.2f}.",
     lambda fig: P.clt_panels(fig, population(), sample_means(), N,
                              "population of waiting times"), tall=True),

AskText(
    prompt=lambda:
        f"The population has sigma = {pop_sigma():.2f} minutes. What is the standard "
        f"error of the mean for a sample of size {N}? Give it to two decimal places.",
    context=lambda: f"sigma = {pop_sigma():.4f}\nn     = {N}\n\n"
                    "standard error = sigma / sqrt(n)",
    answers=[],
    numeric=lambda: (pop_sigma() / np.sqrt(N), 0.02),
    placeholder="a number, e.g. 1.42",
    hint="Divide sigma by the SQUARE ROOT of the sample size. Not by the sample size "
         "itself — that is the classic slip.",
    success=lambda: f"sigma/sqrt(n) = {pop_sigma():.2f}/{np.sqrt(N):.3f} = "
                    f"{pop_sigma()/np.sqrt(N):.2f}, and the simulation gave "
                    f"{R.sd(sample_means()):.2f}. Theory and experiment agree.",
    diagnoses=[
        (r"^\s*0?\.2[0-9]|^\s*0?\.3[0-9]",
         "That looks like sigma divided by n rather than by sqrt(n). Dividing by n "
         "would make error shrink far too fast — take the square root of 30 first, "
         "which is about 5.48."),
    ]),

AskChoice(
    prompt="Your standard error is too big, so you want to HALVE it. What do you have "
           "to do to your sample size?",
    options=[
        "Multiply it by 4",
        "Multiply it by 2",
        "Divide it by 2",
        "Nothing — the standard error does not depend on sample size",
    ],
    correct=0,
    feedback=[
        "Right, and this is why big studies are expensive. Because the n sits under a "
        "square root, you need four times the data to buy twice the precision.",
        "Doubling n divides the error by sqrt(2), about 1.41 — a useful improvement, "
        "but not a halving.",
        "That goes the wrong way. A smaller sample gives you a LARGER standard error.",
        "It very much does: standard error is sigma/sqrt(n), so n is the only part of "
        "it you can control.",
    ],
    success="Precision improves with the square root of effort. Four times the data "
            "for twice the accuracy."),

Show("QQ-checking the simulated means",
     lambda: (lambda m: f"The thousand sample means, put through the normality check "
              f"from last level. The dots sit on the line almost perfectly, and "
              f"IQR/s = {R.iqr_over_s(m):.2f} against a target of 1.3. The means are "
              "normal even though the population they came from was badly "
              "skewed.")(sample_means()),
     lambda fig: P.qqplot(fig, sample_means(), "qqnorm(means)  -  the sample MEANS")),

RDemo("Checking the simulated means",
      'hist(means, breaks = 30)\nqqnorm(means)\nqqline(means)\n\n'
      'IQR(means) / sd(means)',
      lambda: f"[1] {R.sig(R.iqr_over_s(sample_means()), 4)}",
      "The same four checks from Level 4, now applied to a distribution of averages "
      "rather than of people. This is the habit to build: whenever a method assumes "
      "normality, ask WHAT it assumes is normal. From here on it is almost always the "
      "sampling distribution of a statistic, not the raw data."),

Show("How much n you need depends on how ugly the population is",
     "Samples of 5 are still visibly lopsided; by 15 it is nearly symmetric; by 30 it "
     "is hard to tell from a normal curve. For a population this skewed, 30 is about "
     "right — which is exactly where the usual rule of thumb comes from.",
     lambda fig: _n_panels(fig), tall=True),

AskChoice(
    prompt="A hospital's length-of-stay data is strongly right-skewed. A student says "
           "'we cannot use normal methods on it'. What is the accurate reply?",
    options=[
        "The raw stays do not need to be normal — what needs to be roughly normal is "
        "the sampling distribution of the mean, and with n = 200 the CLT delivers that",
        "They are right; skewed data rules out every method in this course",
        "They are right unless you first delete the outliers",
        "It does not matter, because normality is never actually required",
    ],
    correct=0,
    feedback=[
        "Exactly the distinction. The assumption attaches to the statistic, not to the "
        "raw measurements, and that is what the CLT buys you.",
        "That would rule out most real data. The CLT exists precisely so that skewed "
        "populations are still workable once n is reasonable.",
        "Deleting inconvenient data changes what you are studying. The long stays are "
        "real patients, and with a big enough n you do not need to remove them.",
        "Normality IS required — just of the sampling distribution rather than the raw "
        "data. Skipping the check entirely is how people end up with wrong p-values.",
    ],
    success="'Normal' almost always refers to the sampling distribution. Remember that "
            "and half the assumptions in this course stop being mysterious."),

Recap(bullets=[
    "Population (mu, fixed, unknown), sample (x-bar, computed, varies), sampling "
    "distribution (all the x-bars you could have got). Keep these three apart.",
    "The sampling distribution of x-bar is centred on mu, so the sample mean is an "
    "honest estimate of the population mean.",
    "Its spread is the STANDARD ERROR, sigma/sqrt(n). Because of the square root, "
    "quadrupling your sample only halves your error.",
    "Central Limit Theorem: for large enough n (about 30 as a rule of thumb) the "
    "sampling distribution is normal no matter what shape the population had.",
    "So when a method 'assumes normality', it almost always means the sampling "
    "distribution, not your raw data.",
]),
        ])


def _n_panels(fig):
    """Three sample sizes side by side, showing the shape tighten up."""
    from .. import theme as T
    fig.patch.set_facecolor(T.PLOT_BG)
    for j, n in enumerate((5, 15, 30)):
        ax = fig.add_subplot(1, 3, j + 1)
        P.style_axes(ax, f"n = {n}", "sample mean", "count" if j == 0 else "")
        m = sample_means(n=n, reps=NSAMP)
        ax.hist(m, bins=28, color=T.SERIES[j], edgecolor=T.PLOT_BG, alpha=0.9)
        ax.set_xlim(0, 24)
    fig.tight_layout()
