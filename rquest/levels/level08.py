"""LEVEL 8 - Two-sample tests.

Covers: two independent means with large samples (z / zsum.test), two
independent means with small samples and the equal-vs-unequal variance choice
(var.equal = TRUE/FALSE), the paired t-test contrasted against the independent
case, and the two-proportion z-test through prop.test().
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R
from ._common import frame, num

CH = "chol"


def groups():
    """Cholesterol split by smoking habit: two large independent groups."""
    d = frame(CH)
    a = np.asarray(d[d.SMOKE == "sigare"].CHOL, float)
    b = np.asarray(d[d.SMOKE == "nonsmo"].CHOL, float)
    return a, b


def tooth():
    d = frame("tooth")
    return (np.asarray(d[d.supp == "OJ"].len, float),
            np.asarray(d[d.supp == "VC"].len, float))


def sleep_pair():
    d = frame("sleep")
    return (np.asarray(d[d.group == 1].extra, float),
            np.asarray(d[d.group == 2].extra, float))


def small_groups():
    a, b = groups()
    rng = np.random.default_rng(5)
    return (a[rng.choice(len(a), 11, replace=False)],
            b[rng.choice(len(b), 10, replace=False)])


def mort_props():
    d = frame(CH)
    out = []
    for g in ("sigare", "nonsmo"):
        sub = d[d.SMOKE == g]
        out.append((int((sub.MORT == "dead").sum()), len(sub)))
    return out


def build():
    return Level(
        number=8,
        title="Two-sample tests",
        subtitle="Comparing two groups: z, pooled t, Welch t, paired t, two proportions",
        goal="You can now compare two groups and, more importantly, work out which of "
             "the five two-sample tests the situation actually calls for.",
        steps=[

Say("Last level you compared one group against a fixed claim. Far more often the "
    "question is about two groups: does this drug beat that one, do smokers differ "
    "from non-smokers? The logic carries over — but there are now five tests, and "
    "picking the right one is most of the skill.", "talk"),

Explain(
    "The one question that decides everything: independent or paired?",
    "Before anything else, ask whether the two columns of numbers come from DIFFERENT "
    "subjects or the SAME subjects measured twice.\n\n"
    "INDEPENDENT samples: 30 patients on drug A and a different 30 on drug B. Nobody "
    "appears in both groups, and the groups need not even be the same size.\n\n"
    "PAIRED samples: the SAME 30 patients measured before and after. Each number has a "
    "natural partner.\n\n"
    "This is not a detail. Pairing lets you cancel out the differences between "
    "individuals, which usually makes the test far more sensitive. Analysing paired "
    "data as if it were independent throws that advantage away and often misses a "
    "real effect.",
    {
        "independent samples": "two separate groups of subjects, no overlap",
        "paired samples": "one group measured twice, or matched in pairs. The data "
                          "comes in couples",
        "H0 for two samples": "the two population means are equal, i.e. their "
                              "difference is 0",
    }),

Show("Two independent groups",
     lambda: (lambda a, b: f"Cholesterol for {len(a)} cigarette smokers and {len(b)} "
              f"non-smokers — different people in each box. The boxes overlap a lot, "
              f"which is your first hint that the means "
              f"({a.mean():.1f} and {b.mean():.1f}) may not be as far apart as they "
              "look.")(*groups()),
     lambda fig: (lambda a, b: P.boxplot(
         fig, [a, b], labels=["cigarette smokers", "non-smokers"],
         title="boxplot(CHOL ~ SMOKE)", ylabel="cholesterol (mg/dL)"))(*groups())),

RDemo("Two independent means, large samples: the z-test",
      "smokers <- chol$CHOL[chol$SMOKE == \"sigare\"]\n"
      "nonsmok <- chol$CHOL[chol$SMOKE == \"nonsmo\"]\n\n"
      "se <- sqrt(var(smokers)/length(smokers) + var(nonsmok)/length(nonsmok))\n"
      "z  <- (mean(smokers) - mean(nonsmok)) / se\nz\n"
      "2 * (1 - pnorm(abs(z)))",
      lambda: (lambda a, b, r: f"[1] {R.sig(r['z'], 6)}\n[1] {R.sig(r['p'], 6)}")(
          *groups(), R.z_test_two(*groups())),
      "Note the standard error: each group contributes its own variance divided by its "
      "own n, and you add them BEFORE taking the square root. Adding the standard "
      "errors themselves is a common and expensive mistake.\n\n"
      "The == inside square brackets is how you pull one group out of a data frame: "
      "read it as 'keep the CHOL values where SMOKE equals sigare'. If your lab loads "
      "the BSDA package, zsum.test() does the same job from summary statistics."),

Explain(
    "Small samples: pooled t or Welch t?",
    "With small groups you need t instead of z, and R then offers a choice that "
    "confuses everybody:\n\n"
    "    var.equal = TRUE   the POOLED t-test. Assumes both populations have the same "
    "spread, and combines the two sample variances into one better estimate. More "
    "powerful when the assumption holds.\n\n"
    "    var.equal = FALSE  WELCH's t-test. Makes no such assumption and adjusts the "
    "degrees of freedom downwards to compensate — which is why df often comes out as "
    "a decimal.\n\n"
    "Welch is R's DEFAULT, and it is the safer choice: it costs you very little when "
    "the variances really are equal, and it saves you when they are not. Use pooled "
    "only when you have a genuine reason to believe the spreads match, for example a "
    "boxplot showing similar box heights.",
    {
        "pooled variance": "one combined estimate of spread, used when both groups are "
                           "assumed equally variable",
        "Welch's correction": "shrinks the degrees of freedom so the test stays honest "
                              "when spreads differ",
        "var.equal": "the TRUE/FALSE switch in t.test that picks between them",
    }),

RDemo("Both versions, side by side",
      't.test(len ~ supp, data = ToothGrowth)                    # Welch, the default\n'
      't.test(len ~ supp, data = ToothGrowth, var.equal = TRUE)  # pooled',
      lambda: (lambda a, b:
               R.t_test(a, b, data_line="len by supp", group_names=("OJ", "VC"))["text"]
               + "\n" +
               R.t_test(a, b, var_equal=True, data_line="len by supp",
                        group_names=("OJ", "VC"))["text"])(*tooth()),
      lambda: (lambda a, b, w, po:
               f"Same data, two tests. Welch gives df = {w['df']:.3f} (a decimal, "
               f"because the correction is a weighted compromise) and "
               f"p = {R.sig(w['p'], 4)}. Pooled gives a whole-number "
               f"df = {po['df']:.0f} and p = {R.sig(po['p'], 4)}.\n\n"
               "Here they barely differ, because the two groups happen to have similar "
               "spreads. When the spreads differ sharply the two p-values can land on "
               "opposite sides of 0.05, and that is when the choice matters.\n\n"
               "The len ~ supp notation is R's FORMULA syntax: read the squiggle as "
               "'broken down by'. It is tidier than pulling the two groups out by "
               "hand, and you will meet it again in Level 10.")(
          *tooth(), R.t_test(*tooth()), R.t_test(*tooth(), var_equal=True))),

AskText(
    prompt="Two small groups of plants, heights stored in a data frame called plants "
           "with a height column and a group column. Their boxplots show clearly "
           "different spreads. Write the safest t-test command.",
    answers=["t.test(height ~ group, data = plants)",
             "t.test(height ~ group, data = plants, var.equal = FALSE)",
             "re:t\\.test\\(height~group,data=plants(,var\\.equal=f)?\\)"],
    placeholder="t.test(y ~ group, data = ...)",
    hint="Different spreads rules out the pooled version. The safe option is also "
         "R's default, so you may not need to write it out at all.",
    success="Welch is right whenever the spreads look different — and since it is the "
            "default, t.test(height ~ group, data = plants) already gives it. Writing "
            "var.equal = FALSE explicitly is fine and arguably clearer.",
    diagnoses=[
        (r"var\.equal\s*=\s*(TRUE|T)\b",
         "var.equal = TRUE is the POOLED test, which assumes both groups have the same "
         "spread. The boxplots say they do not, so pooling would give you a "
         "misleadingly small p-value."),
        (r"paired\s*=\s*(TRUE|T)",
         "These are two different sets of plants, so the measurements have no natural "
         "partners. paired = TRUE would try to subtract unrelated plants from each "
         "other."),
        (r"t\.test\s*\(\s*plants\s*\)",
         "That hands t.test the whole data frame. Tell it which variable to compare "
         "and which column splits the groups: height ~ group, data = plants."),
        (r"prop\.test",
         "Heights are numeric measurements you average, so this is a test about means."),
    ]),

Show("Paired data: each line is one subject",
     lambda: (lambda a, b: f"The sleep study: the SAME 10 patients measured on two "
              f"drugs. Look at how much the patients differ from each other "
              f"vertically — and yet almost every line slopes the same way. That "
              f"consistency is the signal, and it is only visible because the data is "
              "paired.")(*sleep_pair()),
     lambda fig: (lambda a, b: P.paired_lines(
         fig, a, b, labels=("drug 1", "drug 2"),
         title="sleep: extra hours gained, same 10 patients"))(*sleep_pair())),

RDemo("The paired t-test, and why it matters",
      't.test(extra ~ group, data = sleep, paired = TRUE)\n\n'
      '# the same data analysed WRONGLY as independent:\n'
      't.test(extra ~ group, data = sleep)',
      lambda: (lambda a, b:
               R.t_test(a, b, paired=True, data_line="extra by group")["text"] + "\n" +
               R.t_test(a, b, data_line="extra by group",
                        group_names=("1", "2"))["text"])(*sleep_pair()),
      lambda: (lambda a, b, pr, ind:
               f"Look at what pairing bought. Paired: p = {R.sig(pr['p'], 4)} — clearly "
               f"significant. The same numbers treated as independent: "
               f"p = {R.sig(ind['p'], 4)} — not significant at all.\n\n"
               "Nothing about the data changed. The paired test subtracts each "
               "patient's own first score from their own second score, which cancels "
               "out the fact that some people simply sleep more than others. The "
               "independent test has to fight through all that person-to-person "
               "variation and loses.\n\n"
               "Forgetting paired = TRUE is the single most costly slip in this "
               "level.")(*sleep_pair(), R.t_test(*sleep_pair(), paired=True),
                         R.t_test(*sleep_pair()))),

AskChoice(
    prompt="A gym measures 25 members' weight in January and again in June. Which test "
           "compares the two sets of measurements?",
    options=[
        "t.test(june, january, paired = TRUE)",
        "t.test(june, january)",
        "t.test(june, january, var.equal = TRUE)",
        "prop.test(june, january)",
    ],
    correct=0,
    feedback=[
        "Correct. Each June weight belongs to a specific member who also has a January "
        "weight — the data comes in natural couples, so it is paired.",
        "That treats the June members as a different, unrelated group of people from "
        "the January members. They are the same 25 people, and ignoring that wastes "
        "the pairing.",
        "var.equal is a choice you only make for INDEPENDENT samples. It does not "
        "apply here, and using it still analyses the data as two unrelated groups.",
        "prop.test compares yes/no shares. Weight in kilograms is a numeric "
        "measurement, so this is a test about means.",
    ],
    success="Same subjects measured twice is the definition of paired. Look for words "
            "like 'before and after', 'the same people', or 'matched'."),

RDemo("Two proportions",
      lambda: (lambda g: f"# deaths among smokers vs non-smokers\n"
               f"prop.test(c({g[0][0]}, {g[1][0]}), c({g[0][1]}, {g[1][1]}))")(
          mort_props()),
      lambda: (lambda g: R.prop_test([g[0][0], g[1][0]], [g[0][1], g[1][1]])["text"])(
          mort_props()),
      lambda: (lambda g, r:
               f"Two c() vectors: successes in the first, group sizes in the second, "
               f"in matching order. R reports both sample proportions "
               f"({r['estimate'][0]:.4f} and {r['estimate'][1]:.4f}) and a confidence "
               f"interval for the DIFFERENCE between them.\n\n"
               "That interval is worth reading carefully: if it contains zero, 'no "
               "difference' is a plausible answer and the test will not reject. It is "
               "the same agreement between intervals and tests you saw in Level 7.")(
          mort_props(),
          R.prop_test([mort_props()[0][0], mort_props()[1][0]],
                      [mort_props()[0][1], mort_props()[1][1]]))),

AskText(
    prompt="Campaign A converted 88 of 500 visitors; campaign B converted 120 of 540. "
           "Write the command that tests whether the conversion rates differ.",
    answers=["prop.test(c(88, 120), c(500, 540))",
             "re:prop\\.test\\(c\\(88,120\\),c\\(500,540\\)(,.*)?\\)"],
    placeholder="prop.test(c(x1, x2), c(n1, n2))",
    hint="Two vectors built with c(): all the successes in the first, all the totals "
         "in the second, keeping the campaigns in the same order in both.",
    success=lambda: (lambda r: f"That gives p = {R.sig(r['p'], 4)} with a confidence "
                     f"interval of {R.sig(r['conf_int'][0], 3)} to "
                     f"{R.sig(r['conf_int'][1], 3)} for the difference in rates.")(
        R.prop_test([88, 120], [500, 540])),
    diagnoses=[
        (r"prop\.test\s*\(\s*c\(\s*88\s*,\s*500",
         "You have paired each campaign's successes with its own total inside one "
         "vector. R wants them split by ROLE, not by campaign: c(88, 120) then "
         "c(500, 540)."),
        (r"prop\.test\s*\(\s*88\s*,\s*500\s*\)",
         "That tests campaign A on its own against a default of 0.5. To compare two "
         "campaigns both have to be in the command."),
        (r"0?\.176|0?\.222",
         "Do not convert to proportions yourself — prop.test needs the raw counts so "
         "it knows the sample sizes."),
        (r"t\.test", "Converted-or-not is a yes/no outcome, so each campaign is "
                     "summarised by a proportion, not a mean."),
    ]),

Show("The decision tree for this whole level",
     "Two questions get you to the right test every time: what kind of data, and are "
     "the samples independent or paired? Everything else is a detail R handles.",
     lambda fig: _tree(fig), tall=True),

AskChoice(
    prompt="Researchers compare recovery times (in days) for 14 patients on a new "
           "treatment against 16 different patients on the standard one. Boxplots show "
           "similar spreads. Which command?",
    options=[
        "t.test(new, standard, var.equal = TRUE)",
        "t.test(new, standard, paired = TRUE)",
        "prop.test(c(14, 16), c(30, 30))",
        "A z-test using pnorm",
    ],
    correct=0,
    feedback=[
        "Right on all three counts: numeric data means a mean test, different patients "
        "means independent, small samples mean t, and matching spreads justify the "
        "more powerful pooled version. (Plain Welch would also be defensible.)",
        "14 patients and 16 patients cannot be paired — there is nobody to pair the "
        "two leftover patients with, and the groups are different people anyway.",
        "Recovery time in days is a numeric measurement, not a yes/no outcome. There "
        "are no successes to count here.",
        "With 14 and 16 observations and no known population sigma, z is not "
        "justified. That is exactly the situation t was invented for.",
    ],
    success="Numeric + independent + small + equal spreads = pooled two-sample t."),

Recap(bullets=[
    "First question, always: independent samples (different subjects) or paired (same "
    "subjects twice)? Getting this wrong can hide a real effect completely.",
    "Independent and large: a z-test, with se = sqrt(var1/n1 + var2/n2) — add the "
    "variances over their own n's, then take the root.",
    "Independent and small: t.test(y ~ group, data = d). Welch is the default and the "
    "safe choice; var.equal = TRUE pools and is only justified when the spreads match.",
    "Paired: t.test(a, b, paired = TRUE). It works on each subject's own difference, "
    "which cancels out person-to-person variation and is usually far more sensitive.",
    "Two yes/no groups: prop.test(c(x1, x2), c(n1, n2)) — successes in one vector, "
    "totals in the other, raw counts only.",
]),
        ])


def _tree(fig):
    """A drawn decision tree rather than a wall of text.

    Four rows with generous vertical spacing, so the boxes stay separate even
    when the figure is squeezed on a short laptop screen.
    """
    from .. import theme as T
    import matplotlib.patches as mp
    fig.patch.set_facecolor(T.PLOT_BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(T.PLOT_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    def node(x, y, w, h, text, colour, fs=9.5, weight="normal"):
        ax.add_patch(mp.FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                       boxstyle="round,pad=0.10", linewidth=1.5,
                                       edgecolor=colour, facecolor=T.PANEL_ALT))
        ax.text(x, y, text, ha="center", va="center", color=T.INK, fontsize=fs,
                fontweight=weight, linespacing=1.45)

    def link(x1, y1h, x2, y2h, label=""):
        ax.annotate("", xy=(x2, y2h), xytext=(x1, y1h),
                    arrowprops=dict(arrowstyle="-|>", color=T.INK_DIM, lw=1.4,
                                    shrinkA=2, shrinkB=2))
        if label:
            ax.text((x1 + x2) / 2, (y1h + y2h) / 2 + 0.08, label, color=T.WARN,
                    fontsize=8.5, ha="center", va="bottom")

    # row 1
    node(5.0, 7.35, 4.6, 0.72, "What kind of data?", T.WARN, 11.5, "bold")
    # row 2
    node(2.6, 5.55, 4.2, 0.72, "numbers you average", T.ACCENT)
    node(7.7, 5.55, 3.8, 0.72, "yes / no counts", T.SERIES[2])
    link(5.0, 6.99, 2.6, 5.91)
    link(5.0, 6.99, 7.7, 5.91)
    # row 3
    node(2.6, 3.75, 4.4, 0.72, "independent or paired?", T.ACCENT)
    node(7.7, 3.60, 4.0, 1.05, "prop.test(c(x1, x2),\n          c(n1, n2))",
         T.SERIES[2], 9.5)
    link(2.6, 5.19, 2.6, 4.11)
    link(7.7, 5.19, 7.7, 4.13)
    # row 4 -- three lines per leaf, sized so the text can never outgrow the box
    node(1.55, 1.62, 2.9, 1.70,
         "PAIRED - same subjects\n\nt.test(a, b,\n        paired = TRUE)",
         T.GOOD, 8.8)
    node(5.45, 1.62, 4.5, 1.70,
         "INDEPENDENT - different subjects\n\nlarge n:  z-test\n"
         "small n:  t.test(y ~ g)", T.SERIES[4], 8.8)
    link(2.6, 3.39, 1.55, 2.52, "paired")
    link(2.6, 3.39, 5.45, 2.52, "independent")
    ax.text(5.45, 0.26, "(var.equal = TRUE only when the spreads match)",
            ha="center", color=T.INK_DIM, fontsize=8)
    ax.set_title("Choosing a two-sample test", color=T.INK, fontsize=11.5, pad=4)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.93, bottom=0.03)
