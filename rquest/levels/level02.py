"""LEVEL 2 - Descriptive statistics and outlier detection.

Covers: summary(), var(), sd(), boxplot() and reading outliers off it,
z-scores as a second outlier rule, plot(x, y) for two variables at once,
and sort() / rank().
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R
from ._common import data, frame, num, DIAG_MISSING_DOLLAR

KEY = "chol"


def chol():
    return num(KEY, "CHOL")


def _sd():
    return R.sd(chol())


def _mean():
    return float(chol().mean())


def _z_example():
    """A real high reading from the data, used for the z-score challenge."""
    x = chol()
    return float(np.sort(x)[-6])          # a high but not absurd value


def _flagged():
    out, lo, hi = R.boxplot_outliers(chol())
    return out, lo, hi


def build():
    return Level(
        number=2,
        title="Describing data & outliers",
        subtitle="summary, spread, boxplots, z-scores and scatterplots",
        goal="You can now describe a numeric column in six numbers, measure its "
             "spread, and flag unusual values two different ways.",
        steps=[

Say("Last level you counted labels. The other kind of column holds numbers, and "
    "numbers let you ask better questions: where is the middle, how spread out is "
    "it, and is anything in here weird?", "talk"),

Explain(
    "Centre, spread, and the six-number sketch",
    "Describing a column of 300 numbers means shrinking it to a handful you can hold "
    "in your head. Two things matter: where the values sit (the centre), and how far "
    "they wander from it (the spread).\n\n"
    "R's summary() gives you six numbers that cover both. The QUARTILES in the middle "
    "of that list are the values that cut the sorted data into four equal-sized "
    "quarters.",
    {
        "median": "the middle value once everything is sorted. Half are below it",
        "mean": "the ordinary average: add everything up, divide by how many",
        "Q1 (1st quartile)": "the value a quarter of the way up the sorted data",
        "Q3 (3rd quartile)": "the value three quarters of the way up",
    }),

RDemo("The six-number summary",
      "summary(chol$CHOL)",
      lambda: R.summary(chol()),
      lambda:
      f"Read it left to right: the lowest reading is {R.sig(chol().min())}, a quarter "
      f"of people are below {R.sig(R.quantile(chol(), .25))}, the middle person is at "
      f"{R.sig(float(np.median(chol())))}, and the highest is {R.sig(chol().max())}.\n\n"
      "Mean and median sitting close together, as they do here, is a quiet hint that "
      "the data is roughly symmetric. When the mean is dragged well above the median, "
      "something is stretching the top end."),

AskText(
    prompt="Get the same six numbers for the AGE column instead.",
    answers=["summary(chol$AGE)"],
    placeholder="summary(dataframe$COLUMN)",
    hint="Identical command, different column name after the $.",
    success=lambda: "Which gives:\n\n" + R.summary(num(KEY, "AGE")),
    diagnoses=[
        (r"summary\s*\(\s*AGE\s*\)",
         "AGE does not exist on its own — it is a column inside chol. Write chol$AGE."),
        (r"summary\s*\(\s*chol\s*\)",
         "That summarises all seven columns at once. Useful, but I asked for one: "
         "chol$AGE."),
        (r"\bdescribe\s*\(|\bstats\s*\(",
         "Those come from add-on packages. The one that is built into R and that this "
         "course uses is summary()."),
    ]),

Explain(
    "Two ways to measure spread",
    "VARIANCE measures spread by taking each value's distance from the mean, squaring "
    "it, and averaging those squares. Squaring is what stops the distances above and "
    "below the mean from cancelling out.\n\n"
    "The problem with variance is its units: square the distances and you get squared "
    "units, which is nonsense to report. So we take the square root and get the "
    "STANDARD DEVIATION, which is back in the original units and reads as 'the typical "
    "distance of a value from the mean'.",
    {
        "variance, var()": "average squared distance from the mean. Units are squared",
        "standard deviation, sd()": "square root of the variance. Same units as your "
                                    "data, so you can actually report it",
    }),

RDemo("Variance and standard deviation",
      "var(chol$CHOL)\nsd(chol$CHOL)",
      lambda: f"[1] {R.sig(R.var(chol()), 7)}\n[1] {R.sig(_sd(), 7)}",
      lambda:
      f"The variance is about {R.sig(R.var(chol()), 5)} squared mg/dL, which means "
      f"nothing to anybody. The standard deviation, {R.sig(_sd(), 4)} mg/dL, says "
      "something useful: a typical person sits roughly that far from the average "
      "reading.\n\n"
      "sd(x) is exactly sqrt(var(x)) — you can check it in R if you like."),

AskChoice(
    prompt="A report says 'mean cholesterol 242 mg/dL, variance 3540'. Why would a "
           "statistician rewrite that?",
    options=[
        "Because variance is in squared mg/dL, so the two numbers cannot be compared; "
        "sd (about 59 mg/dL) is in the same units as the mean",
        "Because variance is always wrong and sd is always right",
        "Because 3540 is too large a number to print in a report",
        "Because variance can only be used on categorical data",
    ],
    correct=0,
    feedback=[
        "Exactly. The mean is in mg/dL, so the spread should be too. That is the "
        "entire reason sd exists as a separate thing.",
        "Variance is not wrong — it is the honest engine underneath, and every formula "
        "later in the course uses it. It is just unreadable as a reported quantity.",
        "Size is not the issue. A variance of 4 would be just as awkward to report "
        "next to a mean, because its units are still squared.",
        "The opposite: variance needs numbers to square, so it cannot be used on "
        "categorical data at all.",
    ],
    success="Units are the whole story: report sd, compute with var."),

Explain(
    "How a boxplot is built, and what counts as an outlier",
    "A boxplot is a drawing of five of those summary numbers. The box runs from Q1 to "
    "Q3, so it holds the middle half of the data. The line inside it is the median.\n\n"
    "The whiskers reach out to the furthest value that is still within 1.5 IQRs of the "
    "box. Anything past that gets drawn as its own dot — R's definition of an "
    "OUTLIER. It is a rule of thumb, not a verdict: an outlier is a point worth "
    "looking at, not automatically an error.",
    {
        "IQR": "Q3 minus Q1 — the width of the box, i.e. the span of the middle half",
        "whisker": "the line out to the furthest ordinary value",
        "outlier": "a value more than 1.5 IQRs beyond the box, drawn as a separate dot",
    }),

Show("A boxplot of the cholesterol readings",
     lambda: (lambda o, lo, hi:
              f"The box spans the middle half. The dots above the top whisker are the "
              f"{len(o)} reading(s) R flags as outliers — everything above "
              f"{R.sig(hi, 5)}. Notice how much faster you spot them here than by "
              f"reading 300 numbers.")(*_flagged()),
     lambda fig: P.boxplot(fig, chol(), labels=["CHOL"],
                           title="boxplot(chol$CHOL)", ylabel="cholesterol (mg/dL)")),

RDemo("Drawing the boxplot and listing what it flagged",
      'boxplot(chol$CHOL, main = "Cholesterol", ylab = "mg/dL")\n'
      'boxplot.stats(chol$CHOL)$out',
      lambda: (lambda o, lo, hi:
               (R.format_r_vector(sorted(o)) if len(o) else "numeric(0)") +
               f"\n\n# the fence sits at Q3 + 1.5*IQR = {R.sig(hi, 6)}")(*_flagged()),
      "boxplot() draws it; boxplot.stats(x)$out hands you the actual values that got "
      "drawn as dots, which is what you want when you have to say something about "
      "them in a report."),

AskChoice(
    prompt="On a boxplot, the median line sits much closer to the BOTTOM of the box "
           "than the top. What does that tell you?",
    options=[
        "The lower half of the middle 50% is squeezed together and the upper half is "
        "stretched out — the data is skewed to the right",
        "There is a mistake in the data",
        "The mean equals the median",
        "Exactly half the data is above the box",
    ],
    correct=0,
    feedback=[
        "Right. The median cuts the box into Q1-to-median and median-to-Q3. Each "
        "holds 25% of the data, so if one side is physically wider, those 25% are "
        "spread over a bigger range.",
        "Nothing is wrong. Plenty of real quantities — incomes, waiting times, "
        "reaction times — are genuinely lopsided.",
        "That is what a CENTRED median suggests. An off-centre one suggests the mean "
        "is being pulled away from the median by the long tail.",
        "Half the data is above the MEDIAN. The box itself only holds the middle 50%, "
        "so 25% sits above the box.",
    ],
    success="An off-centre median line is the quickest skewness check there is."),

Explain(
    "z-scores: measuring distance in standard deviations",
    "Is a cholesterol reading of 400 extreme? You cannot say without knowing the "
    "spread. A z-score answers it by rewriting the value as 'how many standard "
    "deviations from the mean is this?'\n\n"
    "    z = (value - mean) / sd\n\n"
    "Now the number carries its own context. z = 0 is exactly average, z = 2 is two "
    "standard deviations above, and a common rule of thumb treats |z| above 3 as an "
    "outlier. Because z has no units, you can compare a cholesterol reading to a "
    "height this way.",
    {
        "z-score": "how many standard deviations a value sits from the mean",
        "|z|": "the size of z ignoring its sign, so it covers both unusually high and "
               "unusually low",
    }),

Show("The same data, before and after converting to z",
     "Converting to z-scores does not change the shape of anything — it just slides "
     "the mean to 0 and restretches the axis so one unit equals one standard "
     "deviation. The red diamonds are values past |z| = 3.",
     lambda fig: P.zscore_strip(fig, chol(), "cholesterol"), tall=True),

RDemo("Computing z-scores for a whole column at once",
      "z <- (chol$CHOL - mean(chol$CHOL)) / sd(chol$CHOL)\n"
      "chol$CHOL[abs(z) > 3]",
      lambda: (lambda z, x:
               (R.format_r_vector(sorted(x[np.abs(z) > 3]))
                if (np.abs(z) > 3).any() else "numeric(0)") +
               f"\n\n# mean = {R.sig(_mean(), 6)}   sd = {R.sig(_sd(), 6)}")(
          R.zscores(chol()), chol()),
      "R does that subtraction and division to EVERY value in the column at once — "
      "you never write a loop. abs(z) > 3 then produces a TRUE/FALSE for each person, "
      "and putting that inside square brackets keeps only the TRUE ones."),

AskText(
    prompt=lambda:
        f"A patient's cholesterol reads {_z_example():.0f} mg/dL. Using the mean "
        f"({R.sig(_mean(), 5)}) and standard deviation ({R.sig(_sd(), 5)}) printed "
        f"above, what is their z-score? Give the number to two decimal places.",
    context=lambda: f"mean(chol$CHOL) = {R.sig(_mean(), 6)}\n"
                    f"sd(chol$CHOL)   = {R.sig(_sd(), 6)}\n"
                    f"patient reading = {_z_example():.0f}",
    answers=[],
    numeric=lambda: ((_z_example() - _mean()) / _sd(), 0.03),
    placeholder="a number, e.g. 1.84",
    hint="Subtract the mean from the reading first, then divide that answer by the "
         "standard deviation. Do it in that order.",
    success=lambda: f"So that reading sits about "
                    f"{(_z_example() - _mean()) / _sd():.2f} standard deviations above "
                    "average — high, but by the |z| > 3 rule not yet an outlier.",
    diagnoses=[
        (r"^\s*-", "Your answer is negative, which would mean the reading is BELOW "
                   "average. Check which way round you did the subtraction: it is "
                   "value minus mean, not mean minus value."),
    ]),

Show("Two variables at once: the scatterplot",
     lambda: f"Each dot is one person: age across, cholesterol up. A scatterplot is "
             f"how you look for a RELATIONSHIP rather than describing one column. "
             f"Here the cloud drifts gently upwards — older people in this sample "
             f"tend to read higher (correlation {R.cor(num(KEY,'AGE'), chol()):.2f}). "
             "Level 10 is where we put a line through a cloud like this.",
     lambda fig: P.scatter(fig, num(KEY, "AGE"), chol(),
                           title="plot(chol$AGE, chol$CHOL)",
                           xlabel="age (years)", ylabel="cholesterol (mg/dL)")),

AskText(
    prompt="Draw a scatterplot with WEIGHT across the bottom and CHOL up the side.",
    answers=["plot(chol$WEIGHT, chol$CHOL)",
             "re:plot\\(chol\\$weight,chol\\$chol(,.*)?\\)"],
    placeholder="plot(x, y)",
    hint="plot() takes the horizontal variable first and the vertical one second, "
         "separated by a comma.",
    success="plot(x, y) always puts the first argument on the horizontal axis. Getting "
            "them the wrong way round is a real mistake, not just cosmetic — it "
            "reverses which variable you are treating as the explanation.",
    diagnoses=[
        (r"plot\s*\(\s*chol\$CHOL\s*,\s*chol\$WEIGHT",
         "You have the axes swapped. The first argument goes across the bottom, so "
         "WEIGHT needs to come first."),
        (r"\bbarplot\s*\(", "barplot() is for counts of categories. Both of these "
                            "columns are numeric, so you want plot()."),
        (r"plot\s*\(\s*chol\$WEIGHT\s*\)",
         "With only one column, plot() draws each value against its row number, which "
         "tells you nothing about cholesterol. Pass both columns."),
        DIAG_MISSING_DOLLAR,
    ]),

RDemo("Ordering values: sort() and rank()",
      "sort(c(50, 10, 40))\nrank(c(50, 10, 40))",
      "[1] 10 40 50\n[1]  3  1  2",
      "These two get confused constantly. sort() returns the VALUES rearranged into "
      "order. rank() leaves everything where it is and tells you each value's "
      "POSITION in that order — the 50 is the 3rd smallest, the 10 is the 1st, the "
      "40 is the 2nd.\n\n"
      "Use sort() when you want to look at the data; use rank() when you need each "
      "case's standing, for example to line it up against another column."),

AskChoice(
    prompt="You have marks <- c(72, 95, 61). What does rank(marks) give?",
    options=["2 3 1", "61 72 95", "3 1 2", "1 2 3"],
    correct=0,
    feedback=[
        "Correct. 72 is the 2nd smallest, 95 is the 3rd, 61 is the 1st — reported in "
        "the original order of the data.",
        "That is what sort(marks) gives: the values themselves, rearranged.",
        "That would be the ranks if the values were 95, 61, 72. Go value by value in "
        "the original order.",
        "That is just the row numbers. rank() only gives 1 2 3 when the data already "
        "happens to be in ascending order.",
    ],
    success="sort() moves the values; rank() reports positions and leaves the order alone."),

Recap(bullets=[
    "summary() gives min, Q1, median, mean, Q3 and max in one line — the fastest "
    "description of a numeric column there is.",
    "var() squares the distances from the mean, so sd() = sqrt(var()) is what you "
    "actually report, because it is in your data's own units.",
    "A boxplot draws the middle half as a box and flags anything past 1.5 IQRs from "
    "it as a dot; boxplot.stats(x)$out lists those values.",
    "A z-score, (x - mean)/sd, rewrites a value as a number of standard deviations, "
    "which makes 'unusual' comparable across different variables. |z| > 3 is the "
    "usual outlier rule.",
    "plot(x, y) draws a scatterplot with x across the bottom; sort() rearranges "
    "values, rank() reports positions.",
]),
        ])
