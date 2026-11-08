"""LEVEL 9 - Chi-square tests.

Covers: why counts need a different test from means, the goodness-of-fit test
on a one-way table, the test of independence on a two-way (contingency) table,
degrees of freedom, and comparing the statistic to a critical value alongside
the p-value shortcut.
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R
from ._common import frame

KEY = "chol"
# A claimed national blood-group split, to test the sample against.
CLAIM_LABELS = ["a", "ab", "b", "o"]
CLAIM_P = [0.40, 0.04, 0.11, 0.45]


def blood_obs():
    labs, cnt = R.table(frame(KEY)["BLOOD"])
    d = {str(l): c for l, c in zip(labs, cnt)}
    return [d.get(l, 0) for l in CLAIM_LABELS]


def gof():
    return R.chisq_gof(blood_obs(), CLAIM_P, data_line="observed")


def tab():
    return R.crosstab(frame(KEY)["SMOKE"], frame(KEY)["MORT"])


def indep():
    m, ra, rb = tab()
    return R.chisq_independence(m, data_line="tbl")


def build():
    return Level(
        number=9,
        title="Chi-square tests",
        subtitle="Testing patterns in counts, not averages",
        goal="You can now test whether a set of counts matches a claimed pattern, and "
             "whether two categorical variables are related.",
        steps=[

Say("Every test since Level 7 has been about a mean or a proportion — numbers you "
    "average or a single yes/no share. Now we go back to the kind of data you counted "
    "in Level 1: whole tables of categories. There is nothing to average, so the test "
    "has to work differently.", "talk"),

Explain(
    "The chi-square idea: observed against expected",
    "Both tests in this level run on exactly the same engine. You write down what you "
    "OBSERVED, work out what you would have EXPECTED if H0 were true, and measure the "
    "gap:\n\n"
    "    chi-square  =  sum of  (observed - expected)squared / expected\n\n"
    "Squaring stops overshoots and undershoots cancelling. Dividing by expected is the "
    "clever part: being 10 off matters enormously in a cell where you expected 12, and "
    "barely at all in one where you expected 900.\n\n"
    "Big chi-square means observed and expected are far apart, which is evidence "
    "against H0. Chi-square can never be negative, so this test is always one-sided.",
    {
        "observed": "the counts you actually have in your data",
        "expected": "the counts H0 predicts you would have seen",
        "chi-square statistic": "the total, size-adjusted gap between the two",
        "one-sided": "only large values count as evidence, so the rejection region is "
                     "the right tail only",
    }),

Explain(
    "Test one: goodness of fit",
    "GOODNESS OF FIT works on a single row of counts. You have a claimed set of "
    "proportions and you ask whether your sample is consistent with them.\n\n"
    "    H0: the population really does split 40% / 4% / 11% / 45%\n"
    "    Ha: at least one of those proportions is wrong\n\n"
    "The expected count for a category is simply the total sample size times that "
    "category's claimed proportion. Degrees of freedom is the number of categories "
    "minus 1 — one is subtracted because once you know the first three counts and "
    "the total, the last one is forced.",
    {
        "goodness of fit": "does one row of counts match a claimed pattern?",
        "expected count": "n times the claimed proportion for that category",
        "df": "number of categories minus 1",
    }),

Show("Observed against expected",
     lambda: (lambda g: f"Blue is what the {int(sum(blood_obs()))} people in the study "
              f"actually are; orange is what the claimed national split predicts. Some "
              f"gaps are bigger than others, and chi-square adds them all up into one "
              f"number: {g['chi']:.3f}.")(gof()),
     lambda fig: (lambda g: P.obs_vs_exp(
         fig, [l.upper() for l in CLAIM_LABELS], g["observed"], g["expected"],
         title="Blood groups: observed vs expected under H0"))(gof())),

RDemo("chisq.test for goodness of fit",
      lambda: ("observed <- table(chol$BLOOD)\nobserved\n\n"
               f"claimed <- c({', '.join(str(p) for p in CLAIM_P)})\n"
               "chisq.test(observed, p = claimed)"),
      lambda: (lambda g: R.format_named([l for l in CLAIM_LABELS],
                                        [str(int(v)) for v in g["observed"]]) +
               "\n" + g["text"])(gof()),
      lambda: (lambda g:
               f"The p = claimed argument is what turns this into a goodness-of-fit "
               f"test. Leave it out and R silently assumes all categories are EQUALLY "
               f"likely, which is a completely different H0.\n\n"
               f"Also worth pulling out: chisq.test(observed, p = claimed)$expected "
               f"prints the expected counts, which is what you show your working with. "
               f"The test needs every expected count to be at least 5 — here the "
               f"smallest is {min(g['expected']):.1f}"
               + (", which is fine." if min(g["expected"]) >= 5 else
                  ", which is marginal, so treat the result with some caution.") +
               "")(gof())),

Show("The decision picture, chi-square style",
     lambda: (lambda g: f"Only the right tail counts. The critical value at "
              f"alpha = 0.05 with df = {g['df']} is {g['critical']:.3f}; our statistic "
              f"is {g['chi']:.3f}. " +
              ("It is past the critical value, so we reject H0 — and note "
               f"p = {R.sig(g['p'], 4)} is below 0.05, which is the same conclusion "
               "reached the quick way."
               if g["chi"] > g["critical"] else
               f"It falls short of the critical value, so we fail to reject H0 — and "
               f"p = {R.sig(g['p'], 4)} is above 0.05, the same conclusion by the "
               "shortcut."))(gof()),
     lambda fig: (lambda g: P.chisq_curve(
         fig, g["chi"], g["df"], title="Goodness of fit: is the gap too big?"))(gof())),

AskChoice(
    prompt="A die is rolled 120 times. To test whether it is fair, what is the "
           "expected count for each face, and what is df?",
    options=[
        "expected 20 each, df = 5",
        "expected 20 each, df = 6",
        "expected 6 each, df = 5",
        "expected 20 each, df = 119",
    ],
    correct=0,
    feedback=[
        "Right: 120 times 1/6 is 20 per face, and df is 6 categories minus 1 = 5.",
        "The expected counts are right, but df is categories MINUS ONE. Once five "
        "counts and the total are known, the sixth is forced — that is the constraint "
        "you subtract.",
        "6 is the number of faces, not the expected count. Expected is n times the "
        "probability: 120 × 1/6 = 20.",
        "119 is n - 1, which is the df for a t-test about a mean. Chi-square df comes "
        "from the number of CATEGORIES, not the sample size.",
    ],
    success="Goodness of fit: expected = n × p, and df = categories - 1."),

AskText(
    prompt="A shop expects its four staff to handle equal shares of sales. The counts "
           "are in a vector called sales. Write the command that tests that claim.",
    answers=["chisq.test(sales)", "re:chisq\\.test\\(sales\\)"],
    placeholder="chisq.test(...)",
    hint="'Equal shares' is exactly the assumption R makes when you do not supply a p "
         "argument, so this one is shorter than you might expect.",
    success="With no p = supplied, chisq.test() tests equal probabilities across all "
            "categories — which is precisely the claim here. If the claim had been "
            "unequal shares you would need p = c(...), and those proportions must "
            "add to 1.",
    diagnoses=[
        (r"p\s*=\s*c\s*\(\s*0?\.25\s*,\s*0?\.25\s*,\s*0?\.25\s*,\s*0?\.25\s*\)",
         "That is correct and R will accept it — but equal probabilities are already "
         "the default, so chisq.test(sales) says the same thing more simply."),
        (r"p\s*=\s*c\s*\(\s*1\s*,\s*1\s*,\s*1\s*,\s*1\s*\)",
         "The p vector must be PROBABILITIES that add up to 1, not counts or weights. "
         "R will stop with an error here."),
        (r"t\.test|prop\.test",
         "Those compare means or a single proportion. Four categories of counts at "
         "once is a chi-square goodness-of-fit problem."),
        (r"table\s*\(\s*sales", "sales is already a vector of counts, so it does not "
                                "need counting again. Pass it straight to chisq.test()."),
    ]),

Explain(
    "Test two: independence",
    "Now two categorical variables at once, laid out as a CONTINGENCY TABLE — smoking "
    "habit down the side, survival across the top.\n\n"
    "    H0: the two variables are independent (knowing one tells you nothing "
    "about the other)\n"
    "    Ha: they are related\n\n"
    "The expected count for a cell assumes independence, which makes it row total "
    "times column total divided by grand total. Degrees of freedom is (rows - 1) times "
    "(columns - 1).\n\n"
    "One warning worth taking seriously: this test can show that two variables move "
    "together. It cannot show that one CAUSES the other.",
    {
        "contingency table": "a grid of counts, one variable down the side and another "
                             "across the top",
        "independent": "knowing a case's row tells you nothing about its column",
        "df for independence": "(number of rows - 1) × (number of columns - 1)",
    }),

RDemo("Building the table and testing it",
      "tbl <- table(chol$SMOKE, chol$MORT)\ntbl\n\nchisq.test(tbl)",
      lambda: (lambda t, i: R.format_crosstab(t[0], t[1], t[2], "SMOKE", "MORT") +
               "\n" + i["text"])(tab(), indep()),
      lambda: (lambda t, i:
               f"table() with TWO columns gives the grid instead of a single row — the "
               f"same function you met in Level 1, doing more work.\n\n"
               f"df = {i['df']} here, from ({t[0].shape[0]} - 1) × "
               f"({t[0].shape[1]} - 1). The critical value at 5% is "
               f"{i['critical']:.3f} against a statistic of {i['chi']:.3f}, and "
               f"p = {R.sig(i['p'], 4)}.\n\n"
               "chisq.test(tbl)$expected is again worth printing: if any expected "
               "count drops below 5, the chi-square approximation gets shaky and you "
               "should either combine categories or use fisher.test() instead.")(
          tab(), indep())),

Show("The same table, drawn",
     lambda: (lambda t, i: f"Column widths show how many people are in each smoking "
              f"group; the split inside each column shows the survival breakdown. If "
              f"the two variables were independent, every column would split at the "
              f"same height. " +
              ("They clearly do not, which is what the test picked up "
               f"(p = {R.sig(i['p'], 4)})." if i["p"] < 0.05 else
               f"They split similarly enough that the test does not reject "
               f"(p = {R.sig(i['p'], 4)})."))(tab(), indep()),
     lambda fig: (lambda t: P.mosaic(fig, t[0], t[1], t[2],
                                     title="Smoking habit against survival"))(tab())),

AskText(
    prompt="A researcher has a data frame survey with columns region and preference, "
           "both categorical. Write the two commands that build the contingency table "
           "and test whether the two variables are related.",
    answers=["tbl <- table(survey$region, survey$preference)\nchisq.test(tbl)",
             "re:tbl=table\\(survey\\$region,survey\\$preference\\)chisq\\.test\\(tbl\\)",
             "chisq.test(table(survey$region, survey$preference))"],
    placeholder="table(...) then chisq.test(...)",
    hint="table() takes BOTH columns this time, separated by a comma. Then hand the "
         "result to chisq.test().",
    success="Either style works — store it in tbl first, or nest it as "
            "chisq.test(table(survey$region, survey$preference)). Storing it is worth "
            "doing when you also want to look at $expected afterwards.",
    diagnoses=[
        (r"chisq\.test\s*\(\s*survey\$region\s*,\s*survey\$preference\s*\)",
         "Passing two separate vectors to chisq.test() actually does work in R, but it "
         "hides what is going on. Build the table first so you can see and check it — "
         "and so you can inspect $expected."),
        (r"table\s*\(\s*survey\s*\)",
         "That hands table() the whole data frame. Name the two columns you want to "
         "cross: table(survey$region, survey$preference)."),
        (r"chisq\.test\s*\(\s*survey\s*\)",
         "chisq.test needs a table of counts, not a data frame. Build the table first."),
        (r"^(?![\s\S]*chisq)", "You built the table but never tested it. Add "
                               "chisq.test(tbl) on a second line."),
    ]),

AskChoice(
    prompt=lambda: (lambda i: f"Our test gave X-squared = {i['chi']:.3f} with "
                    f"df = {i['df']}, critical value {i['critical']:.3f}, and "
                    f"p = {R.sig(i['p'], 4)}. Which conclusion is written correctly?")(
        indep()),
    options=[
        lambda: (lambda i: (
            "At the 5% level there is significant evidence that smoking habit and "
            "survival are related in this population."
            if i["p"] < 0.05 else
            "At the 5% level there is not enough evidence to say smoking habit and "
            "survival are related; the data is consistent with independence."))(indep()),
        "Smoking causes death, and this test proves it.",
        lambda: (lambda i: (
            "The test shows the two variables are independent."
            if i["p"] < 0.05 else
            "The test proves the two variables are related."))(indep()),
        "The chi-square statistic is negative, so we fail to reject H0.",
    ],
    correct=0,
    feedback=[
        lambda: (lambda i: f"Right. It states the level, names both variables, and "
                 f"reports what the evidence supports without overclaiming — "
                 f"p = {R.sig(i['p'], 4)} against alpha = 0.05.")(indep()),
        "This is observational data: smokers may differ from non-smokers in age, diet "
        "and much else. An association is not a cause, and no chi-square test can "
        "make it one.",
        lambda: (lambda i: ("That has the decision backwards — a small p-value is "
                            "evidence AGAINST independence."
                            if i["p"] < 0.05 else
                            "A large p-value is not proof of a relationship, nor "
                            "proof of independence. It just means no evidence of "
                            "one was found."))(indep()),
        "Chi-square adds up squared quantities divided by positive expected counts, so "
        "it can never be negative. If you compute a negative one, you have made an "
        "arithmetic slip.",
    ],
    success="Name both variables, state the level, and never upgrade an association "
            "into a cause."),

Recap(bullets=[
    "Chi-square compares OBSERVED counts with the counts EXPECTED under H0: "
    "sum((O - E)^2 / E). Dividing by E is what makes a gap of 10 matter more in a "
    "small cell than a large one.",
    "Goodness of fit (one row of counts): chisq.test(observed, p = claimed), with "
    "expected = n × p and df = categories - 1. Omit p = and R tests equal likelihood.",
    "Independence (a two-way table): tbl <- table(a, b) then chisq.test(tbl), with "
    "df = (rows - 1)(columns - 1).",
    "The test is one-sided — only a large statistic is evidence — so compare it to the "
    "right-tail critical value, or just read the p-value.",
    "Every expected count should be at least 5; check chisq.test(tbl)$expected. And an "
    "association is never proof of a cause.",
]),
        ])
