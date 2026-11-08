"""LEVEL 7 - Hypothesis testing, one sample.

Covers: framing H0 and Ha in ordinary words BEFORE any formula, the one-sample
z-test, the one-sample t-test, the one-sample proportion test, reading a
p-value against alpha, and writing the conclusion as an English sentence.
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R
from ._common import num, frame

KEY = "chol"
CLAIM = 220.0          # the health authority's claimed national mean
SMALL_N = 14


def chol():
    return num(KEY, "CHOL")


def small():
    rng = np.random.default_rng(21)
    return chol()[rng.choice(len(chol()), SMALL_N, replace=False)]


def dead_counts():
    m = frame(KEY)["MORT"]
    return int((m == "dead").sum()), len(m)


def ztest():
    return R.z_test(chol(), CLAIM, data_line="chol$CHOL")


def build():
    return Level(
        number=7,
        title="One-sample hypothesis tests",
        subtitle="H0, Ha, p-values, and saying what you found in English",
        goal="You can now set up a hypothesis test, choose between z, t and a "
             "proportion test, and turn the p-value into a sentence that means "
             "something.",
        steps=[

Say("A confidence interval answers 'what is it, roughly?'. A hypothesis test answers a "
    "sharper question: 'somebody claimed a specific number — is my data consistent "
    "with that claim?' Same machinery, different question.", "talk"),

Explain(
    "H0 and Ha, before any arithmetic",
    "Every test starts with two competing statements about the POPULATION.\n\n"
    "H0, the null hypothesis, is the boring one: nothing unusual, the claim is true, "
    "there is no difference. It always contains an equals sign.\n\n"
    "Ha, the alternative, is what you suspect instead. It is what you would need "
    "evidence for.\n\n"
    "A test then asks one question only: if H0 were true, how surprising would my "
    "data be? Note the asymmetry — you never prove H0. You either find enough "
    "evidence against it, or you do not. That is why we say 'fail to reject' rather "
    "than 'accept'.",
    {
        "H0 (null)": "the no-change, claim-is-correct statement. Always has =",
        "Ha (alternative)": "what you suspect is true instead",
        "reject H0": "the data would be too surprising if H0 were true",
        "fail to reject H0": "the data is compatible with H0. NOT the same as proving it",
    }),

AskChoice(
    prompt="A manufacturer claims its bags contain 500 g on average. A consumer group "
           "suspects they are underfilled. What are H0 and Ha?",
    options=[
        "H0: mu = 500,  Ha: mu < 500",
        "H0: mu < 500,  Ha: mu = 500",
        "H0: mu = 500,  Ha: mu ≠ 500",
        "H0: x-bar = 500,  Ha: x-bar < 500",
    ],
    correct=0,
    feedback=[
        "Correct. H0 takes the manufacturer's claim at face value, and Ha states the "
        "specific suspicion — underfilling, so the one-sided 'less than'.",
        "Backwards. H0 always carries the equals sign, because the test needs one "
        "exact number to compute 'how surprising is this?' against.",
        "That is the two-sided version, which tests for any difference in either "
        "direction. The group specifically suspects UNDERfilling, so Ha is one-sided.",
        "Hypotheses are always about the POPULATION (mu), never the sample. x-bar is "
        "the number you measured — there is nothing to hypothesise about it.",
    ],
    success="H0 gets the equals sign and the claim; Ha gets the suspicion, and its "
            "direction comes from the wording of the question."),

Explain(
    "The test statistic and the p-value",
    "Next you measure how far your sample sits from H0's claim, in standard errors. "
    "That is the TEST STATISTIC:\n\n"
    "    z  =  (x-bar - claimed mu) / standard error\n\n"
    "A z of 0.4 means your sample landed where H0 expected. A z of 3.5 means it landed "
    "somewhere H0 said was very unlikely.\n\n"
    "The P-VALUE converts that into a probability: if H0 were true, what is the chance "
    "of getting a result at least this extreme? Small p means your data would be "
    "surprising under H0 — so you doubt H0.",
    {
        "test statistic": "how many standard errors your result sits from H0's claim",
        "p-value": "the probability of a result at least this extreme, IF H0 were true",
        "alpha": "the threshold you set in advance, usually 0.05. Small p, reject H0",
    }),

Show("The p-value, drawn",
     lambda: (lambda r: f"The curve is where the test statistic would land if H0 were "
              f"true. The red zones are the most extreme 5% — the rejection region at "
              f"alpha = 0.05. Our statistic, z = {r['z']:.3f}, sits on the orange line. "
              + ("It is out in the red, so the data would be surprising under H0."
                 if abs(r['z']) > 1.96 else
                 "It is not in the red, so the data is compatible with H0."))(ztest()),
     lambda fig: P.test_curve(fig, ztest()["z"], df=None, alpha=0.05,
                              title="One-sample z-test", dist_label="z")),

RDemo("The one-sample z-test, by hand and then in one line",
      lambda: (f"# H0: mu = {CLAIM:g}      Ha: mu != {CLAIM:g}\n\n"
               "xbar <- mean(chol$CHOL)\n"
               "se   <- sd(chol$CHOL) / sqrt(length(chol$CHOL))\n"
               f"z    <- (xbar - {CLAIM:g}) / se\nz\n\n"
               "pvalue <- 2 * (1 - pnorm(abs(z)))\npvalue"),
      lambda: (lambda r: f"[1] {R.sig(r['z'], 6)}\n\n[1] {R.sig(r['p'], 6)}")(ztest()),
      lambda: (lambda r:
               f"The 2 * in the p-value is there because Ha is two-sided — 'different "
               f"from {CLAIM:g}' means surprising in EITHER direction, so you count "
               "both tails. For a one-sided Ha you drop the 2.\n\n"
               f"With n = {len(chol())} this is a large sample, so z is safe. The "
               "BSDA package also offers z.test() if your lab loads it, but the four "
               "lines above are the whole calculation and they always work.")(ztest())),

AskChoice(
    prompt=lambda: (lambda r: f"The p-value came out as {R.sig(r['p'], 4)} and alpha "
                    f"is 0.05. What is the decision?")(ztest()),
    options=[
        lambda: ("Reject H0" if ztest()["p"] < 0.05 else "Fail to reject H0"),
        lambda: ("Fail to reject H0" if ztest()["p"] < 0.05 else "Reject H0"),
        "Accept H0 as proven true",
        "Nothing can be decided without a bigger sample",
    ],
    correct=0,
    feedback=[
        lambda: (lambda r: (f"Right — p = {R.sig(r['p'], 4)} is below 0.05, so a "
                            "result this extreme would be unlikely if H0 were true."
                            if r["p"] < 0.05 else
                            f"Right — p = {R.sig(r['p'], 4)} is above 0.05, so the "
                            "data is perfectly compatible with H0."))(ztest()),
        lambda: (lambda r: f"Compare p = {R.sig(r['p'], 4)} against alpha = 0.05 again "
                 "and check which is bigger. Small p means reject.")(ztest()),
        "You can never accept H0 as proven. Absence of evidence against a claim is "
        "not evidence that the claim is exactly right — the true mean could be a "
        "hair away from it and you would never notice.",
        "The sample is already large, and in any case a test always reaches a "
        "decision. A bigger sample would give you more power, not permission to "
        "decide.",
    ],
    success="Small p, reject H0. Large p, fail to reject. That is the whole decision rule."),

Explain(
    "Which test? It depends on what you have",
    "You now have three one-sample tests, and choosing between them is mechanical:\n\n"
    "    numeric data, n large (30+) or sigma known   ->  z-test\n"
    "    numeric data, n small and sigma unknown      ->  t-test, via t.test()\n"
    "    yes/no data summarised as a proportion       ->  prop.test()\n\n"
    "The first question to ask is always 'what kind of data is this?' Numbers you "
    "average point to z or t; counts of yes/no point to prop.test.",
    {
        "power": "the chance a test detects a real effect. Bigger n, more power",
        "one-sided vs two-sided": "does Ha say 'different' (two) or 'bigger'/'smaller' "
                                  "(one)? Set it with alternative= in R",
    }),

RDemo("The one-sample t-test for a small sample",
      lambda: (f"small <- chol$CHOL[1:{SMALL_N}]\n"
               f"t.test(small, mu = {CLAIM:g})"),
      lambda: R.t_test(small(), mu=CLAIM, data_line="small")["text"],
      lambda: (lambda r:
               f"mu = {CLAIM:g} is how you tell t.test() what H0 claims. Leave it out "
               "and R silently tests against zero, which is almost never the claim you "
               "meant.\n\n"
               "R hands you everything at once: the statistic, the degrees of freedom, "
               "the p-value, and the confidence interval from last level. Note that "
               "the interval and the test always agree — if the claimed value falls "
               "outside the 95% interval, the two-sided test rejects at 5%.")(
          R.t_test(small(), mu=CLAIM))),

Show("The same decision picture, now with a t curve",
     lambda: (lambda r: f"With only {SMALL_N} observations the curve has fatter tails, "
              f"so the critical values sit further out than z's ±1.96 — the test is "
              f"deliberately harder to pass when you have little data. Our statistic "
              f"is t = {r['t']:.3f} on {r['df']:.0f} degrees of freedom, giving "
              f"p = {R.sig(r['p'], 4)}.")(R.t_test(small(), mu=CLAIM)),
     lambda fig: (lambda r: P.test_curve(
         fig, r["t"], df=r["df"], alpha=0.05,
         title=f"One-sample t-test, df = {r['df']:.0f}", dist_label="t"))(
             R.t_test(small(), mu=CLAIM))),

AskText(
    prompt="A machine should fill bottles to 750 ml. You measure 9 bottles into a "
           "vector called fills. Write the command that tests whether the mean has "
           "drifted away from 750.",
    answers=["t.test(fills, mu = 750)", "re:t\\.test\\(fills,mu=750\\)"],
    placeholder="t.test(x, mu = ...)",
    hint="Only 9 bottles and no known sigma, so it is a t-test. The claimed value goes "
         "in the mu argument.",
    success="With n = 9 and sigma unknown, t.test() is right. 'Drifted away' means in "
            "either direction, which is the two-sided default — no alternative= "
            "argument needed.",
    diagnoses=[
        (r"t\.test\s*\(\s*fills\s*\)\s*$",
         "Without mu = 750, R tests H0: mu = 0, which asks whether the bottles are "
         "empty. Add mu = 750."),
        (r"z\.test|pnorm",
         "Nine observations is a small sample and you do not know sigma, so the z-test "
         "is not justified. Use t.test()."),
        (r"mu\s*=\s*fills|t\.test\s*\(\s*750",
         "The data goes first, the claimed value second: t.test(fills, mu = 750)."),
        (r"prop\.test",
         "prop.test is for yes/no counts. Millilitres are numeric measurements, so "
         "this is a test about a MEAN."),
        (r"alternative\s*=\s*[\"']?(less|greater)",
         "'Drifted away' does not name a direction, so it is two-sided — which is "
         "already R's default. Setting alternative= would test only one direction and "
         "could miss a real drift the other way."),
    ]),

RDemo("The one-sample proportion test",
      lambda: (lambda k, n:
               "# H0: p = 0.05   Ha: p != 0.05\n"
               f"# {k} deaths out of {n} people\n"
               f"prop.test({k}, {n}, p = 0.05)")(*dead_counts()),
      lambda: (lambda k, n: R.prop_test(k, n, p=0.05)["text"])(*dead_counts()),
      lambda: (lambda k, n, r:
               f"Same shape of answer as before — a statistic, a p-value and an "
               f"interval — but the statistic is called X-squared here rather than z, "
               f"because prop.test squares the z internally. The decision rule is "
               f"unchanged: p = {R.sig(r['p'], 4)} against alpha.\n\n"
               "p = 0.05 in the command is H0's CLAIMED PROPORTION. Do not confuse it "
               "with the alpha of 0.05 you compare the p-value against — they are "
               "different things that happen to share a number here.")(
          *dead_counts(), R.prop_test(dead_counts()[0], dead_counts()[1], p=0.05))),

Show("A proportion test is a z-test wearing a different hat",
     lambda: (lambda k, n, r:
              f"{k} deaths out of {n} is a sample proportion of {k/n:.4f}, tested "
              f"against H0's claim of 0.05. prop.test reports X-squared = "
              f"{R.sig(r['chi'], 4)}, which is just the square of the equivalent z. "
              f"The shaded rejection region and the p-value work exactly as before.")(
         *dead_counts(), R.prop_test(dead_counts()[0], dead_counts()[1], p=0.05)),
     lambda fig: (lambda k, n: P.test_curve(
         fig, (k / n - 0.05) / ((0.05 * 0.95 / n) ** 0.5), df=None, alpha=0.05,
         title="One-sample proportion test, as a z picture", dist_label="z"))(
             *dead_counts())),

AskChoice(
    prompt="Which of these situations calls for prop.test() rather than t.test()?",
    options=[
        "Asking 340 voters yes/no and testing whether support differs from 50%",
        "Measuring the weight of 40 parcels and testing against a claimed 2.5 kg",
        "Recording 25 reaction times and testing against a published 310 ms",
        "Measuring the height of 60 students and testing against a national average",
    ],
    correct=0,
    feedback=[
        "Right. The raw data is yes/no, and the thing being tested is a SHARE of the "
        "group — that is a proportion.",
        "Weights are numeric measurements you would average, so the parameter is a "
        "mean and the test is t (or z with a big enough sample).",
        "Reaction times are numeric. 25 of them with unknown sigma is a textbook "
        "one-sample t-test.",
        "Heights are numeric measurements, so this is a test about a mean.",
    ],
    success="Yes/no data summarised as a share means a proportion test; numbers you "
            "average mean a mean test."),

Explain(
    "The last step everyone forgets: say it in English",
    "'We reject H0 (p = 0.013)' is not a conclusion — it is a bookkeeping note. A "
    "conclusion names the actual quantity, says what the evidence supports, and stays "
    "readable by somebody who has never taken this course.\n\n"
    "A sentence that gets full marks contains four things: the decision, the "
    "significance level, the real-world quantity, and the direction. For example:\n\n"
    "    'At the 5% level there is significant evidence that the mean fill weight is "
    "below the advertised 500 g.'\n\n"
    "And keep the hedge honest. Failing to reject means the data is compatible with "
    "H0 — not that H0 is true.",
    {
        "statistically significant": "the data would be unlikely under H0. It says "
                                     "nothing about whether the effect is big enough "
                                     "to care about",
        "practical significance": "whether the size of the effect actually matters. A "
                                  "huge sample can make a trivial difference significant",
    }),

AskText(
    prompt=lambda: (lambda r:
        f"Write the conclusion for our cholesterol test as one plain-English sentence. "
        f"The health authority claimed a mean of {CLAIM:g} mg/dL; our sample of "
        f"{len(chol())} people gave a mean of {chol().mean():.1f} with p = "
        f"{R.sig(r['p'], 4)}. Use alpha = 0.05.")(ztest()),
    context=lambda: (lambda r: f"H0: mu = {CLAIM:g}\nHa: mu != {CLAIM:g}\n"
                     f"sample mean = {chol().mean():.2f}\n"
                     f"z = {R.sig(r['z'], 5)}\np-value = {R.sig(r['p'], 5)}\n"
                     f"alpha = 0.05")(ztest()),
    answers=[],
    free=lambda: (lambda r: {
        "must": [
            (["reject", "evidence that", "significant evidence", "conclude"]
             if r["p"] < 0.05 else
             ["fail to reject", "not significant", "no significant", "insufficient",
              "not enough evidence", "consistent with", "compatible with"]),
            ["cholesterol", "mean cholesterol", "average cholesterol", "mean"],
            ["5%", "0.05", "5 percent", "alpha"],
            [f"{CLAIM:g}", "claim", "claimed"],
        ],
        "nice": [["higher", "above", "greater", "lower", "below", "differs",
                  "different"], ["mg/dL", "population"]],
        "avoid": [("proves", "a test never PROVES anything, it weighs evidence"),
                  ("prove", "a test never PROVES anything, it weighs evidence"),
                  ("h0 is true", "you can never conclude H0 is true"),
                  ("accept h0", "say 'fail to reject H0', never 'accept'")],
        "pass": 0.75,
        "model": (
            f"At the 5% significance level there is significant evidence that the mean "
            f"cholesterol of this population differs from the claimed {CLAIM:g} mg/dL, "
            f"and the sample mean suggests it is higher."
            if r["p"] < 0.05 else
            f"At the 5% significance level there is not enough evidence to say the "
            f"mean cholesterol differs from the claimed {CLAIM:g} mg/dL; the data is "
            "consistent with that claim."),
    })(ztest()),
    placeholder="one full sentence  (Ctrl+Enter to submit)",
    hint="Four ingredients: the decision, the significance level, the quantity "
         "(mean cholesterol), and the claimed value you were testing against. Avoid "
         "the word 'prove'.",
    success="That is the sentence a marker is looking for, and the one a non-statistician "
            "can actually act on. Every test in the rest of this course ends here.",
    xp=15),

Recap(bullets=[
    "H0 is the boring claim and always carries the equals sign; Ha is what you "
    "suspect. Both are about the POPULATION, never about your sample.",
    "The test statistic measures how many standard errors your result sits from H0's "
    "claim; the p-value turns that into 'how surprising would this be if H0 were true?'",
    "Decision rule: p below alpha means reject H0, otherwise fail to reject. You never "
    "accept or prove H0.",
    "Choose by the data: large n or known sigma means z; small n with unknown sigma "
    "means t.test(x, mu = claim); yes/no counts mean prop.test(successes, n, p = claim).",
    "Finish every test with an English sentence naming the decision, the level, the "
    "real quantity and the direction.",
]),
        ])
