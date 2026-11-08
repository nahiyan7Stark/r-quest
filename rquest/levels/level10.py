"""LEVEL 10 - Simple linear regression.

Covers: the idea of fitting a line, lm() to build the model, summary() to read
it (coefficients, R-squared, p-values), confint() for the parameters, and -
taught explicitly, because it is the most-confused idea in the whole lab - the
difference between a CONFIDENCE interval and a PREDICTION interval in predict().
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R
from ._common import frame, num

AT = 3.0        # the weight we predict at, in 1000 lbs


def mt():
    return frame("mtcars")


def fit():
    d = mt()
    return R.lm(np.asarray(d.wt, float), np.asarray(d.mpg, float))


def build():
    return Level(
        number=10,
        title="Simple linear regression",
        subtitle="lm(), reading summary(), and confidence vs prediction intervals",
        goal="You can now fit a straight line to two numeric variables, read every "
             "number in summary(), and explain why a prediction interval is always "
             "wider than a confidence interval.",
        steps=[

Say("Back in Level 2 you drew a scatterplot and saw a cloud drifting upwards. We left "
    "it there. This level is where we finally put a line through the cloud and get "
    "something we can predict with.", "happy"),

Explain(
    "Fitting a line, and what 'best' means",
    "A straight line is described by two numbers: where it crosses the vertical axis "
    "(the INTERCEPT) and how steeply it climbs (the SLOPE). You may have written it as "
    "y = mx + c; statisticians write y = b0 + b1x.\n\n"
    "Infinitely many lines could be drawn through a cloud of points, so we need a rule "
    "for 'best'. The rule is LEAST SQUARES: for each point, measure the vertical gap "
    "between it and the line, square those gaps, and pick the line that makes the "
    "total as small as possible. Squaring means big misses are punished much harder "
    "than small ones.",
    {
        "intercept, b0": "the predicted y when x is zero. Sometimes meaningless in "
                         "context, but always needed to place the line",
        "slope, b1": "how much y changes for a one-unit increase in x. This is usually "
                     "the number you care about",
        "residual": "the vertical gap between a real point and the line — what the "
                    "model got wrong for that case",
        "least squares": "the rule that picks the line with the smallest total "
                         "squared residuals",
    }),

Show("The line, and the residuals it is minimising",
     lambda: (lambda f: f"32 cars: weight across, fuel economy up. The orange line is "
              f"the least-squares fit, and the vertical dashes are the residuals it "
              f"is making as small as possible. The fitted line is "
              f"mpg = {f['b0']:.4f} - {abs(f['b1']):.4f} × weight.")(fit()),
     lambda fig: _resid_picture(fig), tall=True),

RDemo("lm() fits it in one line",
      'fit <- lm(mpg ~ wt, data = mtcars)\nfit',
      lambda: (lambda f: "\nCall:\nlm(formula = mpg ~ wt, data = mtcars)\n\n"
               "Coefficients:\n" +
               R.format_named(["(Intercept)", "wt"],
                              R.fmt_common([f["b0"], f["b1"]], 5)) + "\n")(fit()),
      "mpg ~ wt is the FORMULA you met in Level 8. Read the squiggle as 'is explained "
      "by': mpg is explained by wt. The response you are predicting always goes on the "
      "left.\n\n"
      "Printing fit on its own gives you only the two coefficients. Everything "
      "interesting — how certain they are, how much of the variation the line captures "
      "— comes from summary()."),

RDemo("summary() is where the real information is",
      "summary(fit)",
      lambda: R.format_lm_summary(fit(), "mpg ~ wt", "mtcars", "wt"),
      lambda: (lambda f:
               f"Work through it block by block.\n\n"
               f"COEFFICIENTS. Estimate is the slope and intercept. Std. Error is how "
               f"much they would wobble across repeated samples. t value is "
               f"estimate/error, and Pr(>|t|) is the p-value for H0: this coefficient "
               f"is zero. The slope's p-value is the one that matters — it tests "
               f"whether there is any real relationship at all. Here it is "
               f"{R.pval(f['p1'])}, so yes.\n\n"
               f"The stars are a quick visual guide: *** means below 0.001.\n\n"
               f"MULTIPLE R-SQUARED = {f['r2']:.4f}. The share of the variation in mpg "
               f"that the line accounts for — about {f['r2']*100:.0f}%. The rest is "
               f"everything weight does not explain.\n\n"
               f"RESIDUAL STANDARD ERROR = {f['s']:.3f}. The typical size of a miss, "
               f"in mpg. That is the number to quote when somebody asks how accurate "
               f"the model is.")(fit())),

AskChoice(
    prompt=lambda: (lambda f: f"The slope came out as {f['b1']:.4f}. What does that "
                    "number mean in plain English?")(fit()),
    options=[
        lambda: (lambda f: f"Each extra 1000 lbs of weight is associated with about "
                 f"{abs(f['b1']):.2f} fewer miles per gallon")(fit()),
        lambda: (lambda f: f"A car weighing 1000 lbs does {abs(f['b1']):.2f} miles "
                 "per gallon")(fit()),
        lambda: (lambda f: f"{abs(f['b1']):.0f}% of cars are heavy")(fit()),
        lambda: (lambda f: f"Adding weight CAUSES a drop of exactly "
                 f"{abs(f['b1']):.2f} mpg in every car")(fit()),
    ],
    correct=0,
    feedback=[
        "Right. A slope is always 'change in y per one-unit change in x', and the unit "
        "of x here is 1000 lbs. The negative sign says heavier means thirstier.",
        "That describes a point ON the line, not the slope. To get a predicted mpg at "
        "a given weight you substitute into b0 + b1x.",
        "A slope is not a percentage — it is a rate of change, in the units of the two "
        "variables involved.",
        "Two problems. 'Exactly' is wrong: this is an average trend and individual "
        "cars scatter around it. And 'causes' is wrong: this is observational data, "
        "and heavier cars also tend to have bigger engines.",
    ],
    success="Slope = change in y for a one-unit change in x. Always say it with the "
            "units attached."),

RDemo("confint(): how uncertain are the slope and intercept?",
      "confint(fit)\nconfint(fit, level = 0.99)",
      lambda: (lambda f: R.confint_lm(f, xname="wt") + "\n\n" +
               R.confint_lm(f, level=0.99, xname="wt"))(fit()),
      lambda: (lambda f, ci:
               f"These are ordinary confidence intervals, exactly as in Level 6, but "
               f"for the two coefficients rather than for a mean.\n\n"
               f"The slope's interval is {ci[0]} to {ci[1]}. Because it does not "
               "contain zero, we can be 95% confident the true slope is genuinely "
               "negative — which is the same information the slope's p-value gave, "
               "just expressed as a range instead of a decision.\n\n"
               "And the 99% version is wider, for the reason you already know.")(
          fit(), R.fmt_common([fit()["b1"] - R.qt(.975, fit()["df"]) * fit()["se_b1"],
                               fit()["b1"] + R.qt(.975, fit()["df"]) * fit()["se_b1"]],
                              6))),

Explain(
    "The distinction the lab always catches people on",
    "You now ask the model about a car weighing 3000 lbs. There are TWO different "
    "questions hiding in that, and predict() answers whichever one you ask for.\n\n"
    "CONFIDENCE interval — 'what is the AVERAGE mpg of all cars weighing 3000 lbs?' "
    "You are asking about the position of the line itself. The only uncertainty is in "
    "where the line sits.\n\n"
    "PREDICTION interval — 'my neighbour's car weighs 3000 lbs. What will IT do?' Now "
    "there are two sources of uncertainty: where the line sits, AND how far that "
    "particular car scatters from the line.\n\n"
    "Two sources of uncertainty rather than one means the prediction interval is "
    "ALWAYS wider. If you ever compute one that is narrower, you have mixed them up.",
    {
        "confidence interval (regression)": "a range for the MEAN y of everyone at "
                                            "this x. About the line",
        "prediction interval": "a range for ONE NEW individual at this x. About a "
                               "single case, so it is always wider",
        "which do I want?": "asking about a group average, use confidence; asking "
                            "about one specific new case, use prediction",
    }),

Show("Both bands on one picture",
     lambda: (lambda f, c, p:
              f"The narrow green band is the confidence band — where the LINE could "
              f"be. The wide red band is the prediction band — where an individual "
              f"CAR could be. At weight = {AT:g} the confidence interval runs "
              f"{c[1]:.2f} to {c[2]:.2f} (width {c[2]-c[1]:.2f}), while the prediction "
              f"interval runs {p[1]:.2f} to {p[2]:.2f} (width {p[2]-p[1]:.2f}).\n\n"
              "Notice too that both bands are narrowest in the middle and flare out at "
              "the edges — the model is least sure about x values far from the average.")(
         fit(), R.predict_lm(fit(), AT, interval="confidence"),
         R.predict_lm(fit(), AT, interval="prediction")),
     lambda fig: P.regression_bands(
         fig, fit(), xlabel="weight (1000 lbs)", ylabel="miles per gallon",
         title="Confidence band vs prediction band", at=AT), tall=True),

RDemo("predict(), both ways",
      f'newcar <- data.frame(wt = {AT:g})\n\n'
      'predict(fit, newcar, interval = "confidence")\n'
      'predict(fit, newcar, interval = "prediction")',
      lambda: (R.format_predict(fit(), AT, interval="confidence") + "\n\n" +
               R.format_predict(fit(), AT, interval="prediction")),
      lambda: (lambda f, c, p:
               "Both give the same fit — the point estimate is identical, because both "
               "sit on the same line. Only the lwr and upr columns differ.\n\n"
               f"The new x value has to arrive as a DATA FRAME whose column is named "
               f"exactly as in the formula (wt here). Passing a bare number is the "
               "most common error, and R's complaint about it is not very "
               "informative.\n\n"
               f"Width comparison: {c[2]-c[1]:.2f} against {p[2]-p[1]:.2f}. The "
               "prediction interval is roughly three times wider, and that gap is the "
               "individual car's own scatter.")(
          fit(), R.predict_lm(fit(), AT, interval="confidence"),
          R.predict_lm(fit(), AT, interval="prediction"))),

AskText(
    prompt="A dealer asks: 'I have one specific used car here that weighs 2,500 lbs — "
           "what mileage should I expect from IT?' Write the predict() command that "
           "answers exactly that question.",
    context="fit <- lm(mpg ~ wt, data = mtcars)\n# wt is measured in thousands of lbs",
    answers=['predict(fit, data.frame(wt = 2.5), interval = "prediction")',
             're:predict\\(fit,(newdata=)?data\\.frame\\(wt=2\\.5\\),interval="prediction"\\)'],
    placeholder='predict(model, data.frame(x = value), interval = "...")',
    hint="One specific car, not the average of all cars at that weight. And 2,500 lbs "
         "is 2.5 in these units.",
    success="One individual case means a PREDICTION interval. The dealer wants to know "
            "what this car will do, not what cars of this weight do on average — and "
            "the honest answer is a much wider range than most people expect.",
    diagnoses=[
        (r'interval\s*=\s*["\']confidence',
         "That answers the AVERAGE question: 'what do 2,500 lb cars do on average?'. "
         "The dealer is asking about one specific car sitting in the lot, which needs "
         'interval = "prediction" and gives a considerably wider range.'),
        (r"predict\s*\(\s*fit\s*,\s*2\.5",
         "The new x value has to be wrapped in a data frame whose column name matches "
         "the formula: data.frame(wt = 2.5). A bare number will not work."),
        (r"data\.frame\s*\(\s*2500|wt\s*=\s*2500",
         "Check the units. wt in mtcars is in THOUSANDS of pounds, so 2,500 lbs is "
         "2.5, not 2500. Feeding in 2500 asks the model about a car weighing two and "
         "a half million pounds."),
        (r"data\.frame\s*\(\s*(x|weight|mpg)\s*=",
         "The column in your new data frame must be named exactly as it is in the "
         "formula — wt, not x or weight."),
        (r"^\s*predict\s*\(\s*fit\s*\)\s*$",
         "With no new data, predict() just returns the fitted values for the original "
         "32 cars. You need to hand it the new weight."),
    ],
    xp=15),

AskChoice(
    prompt="Which statement about the two intervals is TRUE?",
    options=[
        "A prediction interval is always wider than a confidence interval at the same "
        "x, because it includes an individual case's own scatter as well as "
        "uncertainty about the line",
        "They are the same width; only the wording differs",
        "A confidence interval is wider, because it covers every car rather than just "
        "one",
        "A prediction interval is wider only when R-squared is low",
    ],
    correct=0,
    feedback=[
        "Exactly. One source of uncertainty versus two. That is the whole reason for "
        "the difference, and it holds at every x.",
        "They share a centre but never a width. Compare the lwr and upr columns in the "
        "two predict() outputs — they are quite different.",
        "Backwards, and the intuition behind it is the trap. Averaging over many cars "
        "makes the estimate MORE precise, not less, because individual scatter cancels "
        "out. Predicting one car has nothing to cancel.",
        "It is wider at every x and at every R-squared. A low R-squared widens BOTH "
        "bands; it does not create the gap between them.",
    ],
    success="Two sources of uncertainty beat one, always. Prediction is always wider."),

Show("One last check: are the residuals well behaved?",
     "Residuals against fitted values. You want a shapeless cloud around the zero "
     "line. A curve would mean a straight line was the wrong shape; a funnel widening "
     "to the right would mean the scatter grows with x, which breaks one of "
     "regression's assumptions. This one is acceptable, with a mild hint of curvature "
     "at the extremes.",
     lambda fig: P.residual_plot(fig, fit(), "fitted mpg")),

Recap(bullets=[
    "lm(y ~ x, data = d) fits the least-squares line; read the squiggle as 'is "
    "explained by' and put the variable you are predicting on the left.",
    "summary(fit) gives it all: Estimate (slope and intercept), Pr(>|t|) for the "
    "slope (is there a real relationship?), Multiple R-squared (share of variation "
    "explained), and Residual standard error (typical size of a miss).",
    "The slope means 'change in y for a one-unit change in x'. Quote it with units, "
    "and do not upgrade it into a cause.",
    "confint(fit) gives confidence intervals for the coefficients. A slope interval "
    "that excludes zero means a significant relationship.",
    "predict() needs a DATA FRAME with the same column name as the formula. "
    'interval = "confidence" answers about the AVERAGE y at that x; '
    'interval = "prediction" answers about ONE NEW case and is always wider.',
]),
        ])


def _resid_picture(fig):
    from .. import theme as T
    f = fit()
    ax = P.new_axes(fig, "Least squares: minimising the total squared vertical gap",
                    "weight (1000 lbs)", "miles per gallon")
    x, y, yhat = f["x"], f["y"], f["fit"]
    for xi, yi, hi in zip(x, y, yhat):
        ax.plot([xi, xi], [yi, hi], color=T.BAD, lw=1.0, alpha=0.65)
    ax.scatter(x, y, s=34, color=T.SERIES[0], zorder=3, edgecolor=T.PLOT_BG, lw=0.5)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, f["b0"] + f["b1"] * xs, color=T.WARN, lw=2.4,
            label=f"mpg = {f['b0']:.3f} {'-' if f['b1'] < 0 else '+'} "
                  f"{abs(f['b1']):.3f} x wt")
    ax.legend(facecolor=T.PANEL_ALT, edgecolor=T.PLOT_GRID, labelcolor=T.INK, fontsize=9)
