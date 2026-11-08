"""BOSS CHALLENGE - one open question, no worked example.

The player gets a dataset held back from all ten levels (iris) and a question
nobody has broken into steps for them.  They must, on their own:

    load it  ->  describe it  ->  visualise it  ->  choose the right test
             ->  run it  ->  read the output  ->  write a conclusion in English

Every stage chains a skill from a different earlier level (1, 2, 8, 7, 10's
reading discipline).  Grading is deliberately generous on wording but strict on
the three things that actually matter: the right test was chosen, the p-value
was read the right way round, and the conclusion is in plain language.
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R
from ._common import data, frame

# tkinter is imported inside _finish() rather than here, so that the level
# content stays importable (and testable) without a display.

KEY = "iris"
A, B = "versicolor", "virginica"
COL = "Sepal.Width"


def groups():
    d = frame(KEY)
    return (np.asarray(d[d.Species == A][COL], float),
            np.asarray(d[d.Species == B][COL], float))


def test():
    a, b = groups()
    return R.t_test(a, b, data_line=f"{COL} by Species", group_names=(A, B))


def build():
    return Level(
        number=11,
        kicker="BOSS CHALLENGE",
        title="The Open Question",
        subtitle="A dataset you have not seen, and nobody to break it into steps",
        goal="",
        on_finish=_finish,
        steps=[

Say("This is the part I cannot help you with. New dataset, one real question, and no "
    "worked example first. Everything you need is something you already did in an "
    "earlier level — the job now is knowing which one to reach for.", "think"),

Explain(
    "Your brief",
    lambda: (lambda ds:
             f"The dataset is iris: {len(ds.df)} flowers, three species, with four "
             f"measurements each. It is loaded {('live from ' + ds.spec.url) if ds.source == 'url' else 'from the bundled offline copy'}.\n\n"
             f"THE QUESTION\n\n"
             f"    Is the average {COL.replace('.', ' ').lower()} different between "
             f"the {A} and {B} species?\n\n"
             f"Work through it the way a statistician would: load the data, describe "
             f"it, look at it, choose a test, run it, read the output, and answer the "
             f"question in a sentence. Seven stages. Take your time — a wrong answer "
             f"here still costs you nothing.")(data(KEY)),
    {
        "your job": "decide what to do, not just how to type it",
        "the marks": "the test you choose, how you read the p-value, and whether your "
                     "conclusion is readable by a non-statistician",
    }),

# ---- stage 1: load ------------------------------------------------------
AskText(
    prompt="STAGE 1 of 7 — LOAD.  iris is one of the datasets built into R itself. "
           "Write the command that makes it available in your session.",
    context="# nothing is loaded yet",
    answers=["data(iris)", "data('iris')", "library(datasets)\ndata(iris)"],
    placeholder="data(...)",
    hint="Built-in datasets do not need downloading. One function, one argument.",
    success=lambda: "iris is now available. (If it had been a file on the web instead, "
                    "this would have been the read.csv() line from Level 1 — "
                    'read.csv("https://.../iris.csv").)',
    diagnoses=[
        (r"read\.csv|read\.table",
         "That is the right instinct for a file, but iris ships inside R — there is "
         "nothing to download. The function for a built-in dataset is data()."),
        (r"^\s*iris\s*$",
         "Typing iris would print all 150 rows. First make it available with data()."),
        (r"library\s*\(\s*iris",
         "iris is a dataset, not a package. library() loads packages; data() loads "
         "datasets."),
        (r"install\.packages",
         "Nothing to install — iris comes with base R. Just data(iris)."),
    ],
    xp=10),

# ---- stage 2: describe --------------------------------------------------
AskText(
    prompt=f"STAGE 2 of 7 — DESCRIBE.  Before testing anything, get the mean "
           f"{COL} for EACH species. One command.",
    context="head(iris)\n" + (lambda: data(KEY).r_head(4))(),
    answers=[f"tapply(iris${COL}, iris$Species, mean)",
             f"re:tapply\\(iris\\$sepal\\.width,iris\\$species,mean\\)",
             f"aggregate({COL} ~ Species, data = iris, FUN = mean)",
             f"re:aggregate\\(sepal\\.width~species,data=iris,(fun=)?mean\\)",
             f"by(iris${COL}, iris$Species, mean)"],
    placeholder="tapply(values, groups, function)",
    hint="You want one number per species. tapply() splits a column by a grouping "
         "column and applies a function to each piece: tapply(values, groups, mean).",
    success=lambda: (lambda d: "That gives:\n\n" + R.format_named(
        [A, B], R.fmt_common([groups()[0].mean(), groups()[1].mean()], 5)) +
        f"\n\nA gap of about {abs(groups()[1].mean() - groups()[0].mean()):.3f} cm. "
        "Whether that is real or just sampling noise is exactly what the rest of this "
        "challenge decides.")(frame(KEY)),
    diagnoses=[
        (r"^\s*mean\s*\(\s*iris\$",
         "That averages ALL 150 flowers together, mixing the three species into one "
         "number. You need the mean within each species separately."),
        (r"^\s*summary\s*\(\s*iris\s*\)\s*$",
         "summary(iris) describes every column across all species at once — useful, "
         "but it will not give you a mean per species. You need to split by group."),
        (r"tapply\s*\(\s*iris\$Species",
         "Arguments are the wrong way round: the VALUES you want averaged come first, "
         "then the column that defines the groups."),
        (r"table\s*\(",
         "table() counts categories. Sepal width is numeric, so the summary you want "
         "is a mean, not a count."),
        (r"tapply\s*\([^,]+,[^,]+\)\s*$",
         "tapply needs three things: the values, the grouping column, and WHICH "
         "function to apply. Add mean as the third argument."),
    ],
    xp=10),

# ---- stage 3: visualise -------------------------------------------------
AskText(
    prompt=f"STAGE 3 of 7 — VISUALISE.  Draw a plot that lets you compare the "
           f"{COL} distributions of the species side by side.",
    context=lambda: R.format_named(
        [A, B], R.fmt_common([groups()[0].mean(), groups()[1].mean()], 5)),
    answers=[f"boxplot({COL} ~ Species, data = iris)",
             f"re:boxplot\\(sepal\\.width~species,data=iris(,.*)?\\)",
             f"re:boxplot\\(iris\\$sepal\\.width~iris\\$species(,.*)?\\)"],
    placeholder="boxplot(y ~ group, data = ...)",
    hint="Comparing the spread of a numeric variable across groups is exactly what a "
         "boxplot is for, and the formula notation from Level 8 splits it by species "
         "automatically.",
    success="Boxplots side by side is the standard first look before a two-group "
            "comparison — it shows you the centres, the spreads and any outliers in "
            "one picture, and the spreads are what decide your var.equal choice.",
    diagnoses=[
        (r"\bhist\s*\(", "A histogram shows one distribution at a time, so you would "
                         "have to draw three and flip between them. A boxplot puts "
                         "them side by side on one axis."),
        (r"\bplot\s*\(\s*iris\$Sepal\.Width\s*,\s*iris\$Species",
         "A scatterplot needs two NUMERIC variables. Species is a category, so this "
         "is a groups comparison — use a boxplot."),
        (r"barplot\s*\(", "barplot() draws counts of categories. Sepal width is a "
                          "numeric measurement with a whole distribution behind it, "
                          "which a single bar would throw away."),
        (r"boxplot\s*\(\s*iris\s*\)",
         "That draws a box for every numeric column in the data frame, all species "
         "mixed together. Use the formula to split one column by species: "
         f"boxplot({COL} ~ Species, data = iris)."),
    ],
    xp=10),

Show("Here is what that draws",
     lambda: (lambda a, b: f"Three species; the two you care about are the second and "
              f"third. Their boxes overlap but {B} clearly sits higher, and the box "
              f"HEIGHTS look similar — sd {R.sd(a):.3f} against {R.sd(b):.3f} — which "
              "is information you will want in a moment.")(*groups()),
     lambda fig: _species_box(fig)),

# ---- stage 4: choose the test ------------------------------------------
AskChoice(
    prompt=f"STAGE 4 of 7 — CHOOSE.  Two species, 50 flowers each, different "
           f"flowers in each group, comparing an average. Which test?",
    context=lambda: (lambda a, b:
                     f"n = {len(a)} {A}, n = {len(b)} {B}\n"
                     f"means  {a.mean():.3f}  and  {b.mean():.3f}\n"
                     f"sds    {R.sd(a):.3f}  and  {R.sd(b):.3f}\n"
                     "different flowers in each group")(*groups()),
    options=[
        "A two-sample t-test on independent samples",
        "A paired t-test",
        "A one-sample t-test against a claimed value",
        "A chi-square test of independence",
    ],
    correct=0,
    feedback=[
        "Right. Numeric measurement, two groups, different subjects in each — that is "
        "the independent two-sample t-test from Level 8. (With n = 50 per group a "
        "z-test would also be defensible; R's t.test is the standard answer.)",
        "Paired needs each flower in one group to have a partner in the other. These "
        "are 100 completely different flowers, so there is nothing to pair them by — "
        "and a paired test would demand equal group sizes and subtract unrelated "
        "flowers from each other.",
        "One-sample compares ONE group against a fixed claimed number. Here you have "
        "two groups and no external claim to test against.",
        "Chi-square works on COUNTS of categories. Sepal width is a numeric "
        "measurement you average, so this is a test about means.",
    ],
    success="Numeric + two groups + independent = two-sample t-test.",
    xp=15),

# ---- stage 5: run it ----------------------------------------------------
AskText(
    prompt=f"STAGE 5 of 7 — RUN IT.  Write the command. The data frame is iris, and "
           f"you need only the {A} and {B} rows — the subset argument does that for "
           f"you, or you may build the two vectors yourself.",
    context=f'# hint: subset = Species != "setosa"   keeps the two species you want',
    answers=[
        f't.test({COL} ~ Species, data = iris, subset = Species != "setosa")',
        f're:t\\.test\\(sepal\\.width~species,data=iris,subset=species!="setosa"\\)',
        f're:t\\.test\\(sepal\\.width~species,data=iris\\[iris\\$species!="setosa",\\]\\)',
        f're:t\\.test\\(iris\\$sepal\\.width\\[iris\\$species=="{A}"\\],'
        f'iris\\$sepal\\.width\\[iris\\$species=="{B}"\\]\\)',
    ],
    placeholder='t.test(y ~ group, data = iris, subset = ...)',
    hint="Formula notation from Level 8: t.test(value ~ group, data = ...). The "
         "subset argument keeps only the rows you want, and != means 'is not equal to'.",
    success=lambda: "Which prints:\n\n" + test()["text"],
    diagnoses=[
        (r"var\.equal\s*=\s*(TRUE|T)\b",
         "Defensible — the two spreads really are similar here, so pooling is "
         "justified and gives nearly the same answer. But Welch is R's default and "
         "the safer habit, so I am looking for the command without it."),
        (r"paired\s*=\s*(TRUE|T)",
         "These are different flowers in each group, so there is nothing to pair. "
         "Drop paired = TRUE."),
        (r't\.test\s*\(\s*Sepal\.Width\s*~\s*Species\s*,\s*data\s*=\s*iris\s*\)\s*$',
         "Close, but without the subset R tries to compare all THREE species at once, "
         "and t.test can only handle two groups — it stops with an error. Add "
         'subset = Species != "setosa".'),
        (r"aov\s*\(|anova",
         "ANOVA compares three or more groups and is beyond this course. The question "
         "names exactly two species, so a two-sample t-test is the right tool."),
        (r"mu\s*=",
         "mu = is for a ONE-sample test against a claimed value. With two groups, H0 "
         "is that the two means are equal, which is already t.test's default."),
        (r"prop\.test",
         "prop.test compares yes/no shares. Sepal width is a numeric measurement."),
    ],
    xp=15),

# ---- stage 6: read the output ------------------------------------------
AskText(
    prompt=lambda: (lambda r: f"STAGE 6 of 7 — READ IT.  From that output, what is "
                    f"the p-value? Type just the number.")(test()),
    context=lambda: test()["text"],
    answers=[],
    numeric=lambda: (test()["p"], test()["p"] * 0.06 + 1e-9),
    placeholder="0.00xxxx",
    hint="It is on the same line as t and df, labelled p-value. Copy it exactly as R "
         "printed it.",
    success=lambda: (lambda r: f"p = {R.sig(r['p'], 4)}. Against alpha = 0.05 that is "
                     + ("clearly below the threshold, so H0 — 'the two species have "
                        "the same mean sepal width' — is rejected."
                        if r["p"] < 0.05 else
                        "above the threshold, so we fail to reject H0.")
                     + " Note the confidence interval agrees: it "
                     + ("excludes" if r["p"] < 0.05 else "includes")
                     + " zero.")(test()),
    diagnoses=[
        (r"^\s*-?3\.2|^\s*3\.2", "That is the t statistic, not the p-value. Look "
                                 "further along the same line."),
        (r"^\s*97", "That is the degrees of freedom. The p-value is the last item on "
                    "that line."),
        (r"^\s*0?\.05\s*$", "0.05 is alpha, the threshold you compare AGAINST. The "
                            "p-value is the number R computed from your data."),
    ],
    xp=10),

# ---- stage 7: conclusion in English ------------------------------------
AskText(
    prompt=lambda: (lambda r:
        f"STAGE 7 of 7 — CONCLUDE.  Answer the original question in one plain-English "
        f"sentence a biologist with no statistics training could act on. Say what you "
        f"found, at what level, about which quantity, and in which direction.")(test()),
    context=lambda: (lambda a, b, r:
        f"question   is mean {COL} different between {A} and {B}?\n"
        f"means      {a.mean():.3f} ({A})   vs   {b.mean():.3f} ({B})\n"
        f"t = {R.sig(r['t'], 5)}   df = {R.sig(r['df'], 5)}   p = {R.sig(r['p'], 5)}\n"
        f"95% CI for the difference   {R.sig(r['conf_int'][0], 4)} to "
        f"{R.sig(r['conf_int'][1], 4)}\nalpha = 0.05")(*groups(), test()),
    answers=[],
    free=lambda: (lambda r: {
        "must": [
            (["significant", "reject", "evidence that", "conclude", "difference"]
             if r["p"] < 0.05 else
             ["fail to reject", "no significant", "not significant", "insufficient",
              "no evidence", "consistent with"]),
            ["sepal width", "sepal.width", "sepal"],
            ["versicolor", "virginica"],
            ["5%", "0.05", "5 percent", "alpha", "significance level"],
        ],
        "nice": [["wider", "narrower", "higher", "lower", "greater", "larger",
                  "smaller", "broader"],
                 ["mean", "average"],
                 ["cm", "0.20", "0.2"]],
        "avoid": [("proves", "a test weighs evidence, it never proves"),
                  ("prove", "a test weighs evidence, it never proves"),
                  ("causes", "this is observational data; it shows a difference, "
                             "not a cause"),
                  ("accept h0", "say 'fail to reject H0', never 'accept'")],
        "pass": 0.75,
        "model": (
            f"At the 5% significance level there is significant evidence that mean "
            f"sepal width differs between versicolor and virginica, with virginica "
            f"averaging about 0.20 cm wider."
            if r["p"] < 0.05 else
            f"At the 5% significance level there is not enough evidence to say mean "
            f"sepal width differs between versicolor and virginica."),
    })(test()),
    placeholder="one full sentence  (Ctrl+Enter to submit)",
    hint="Four things a marker looks for: the decision, the significance level, the "
         "quantity (mean sepal width), and the two species — plus the direction if "
         "you found a difference. Avoid 'proves' and 'causes'.",
    success="That is a conclusion somebody can actually use. You have just taken a "
            "dataset you had never seen to a defensible, readable answer without a "
            "single worked example — which is the entire point of the course.",
    xp=20),
        ])


def _species_box(fig):
    d = frame(KEY)
    order = ["setosa", A, B]
    P.boxplot(fig, [np.asarray(d[d.Species == s][COL], float) for s in order],
              labels=order, title=f"boxplot({COL} ~ Species, data = iris)",
              ylabel="sepal width (cm)")


# ==========================================================================
# the boss's own result screen
# ==========================================================================

STAGE_NAMES = ["Load the data", "Describe it by group", "Visualise it",
               "Choose the right test", "Run the test", "Read the p-value",
               "Write the conclusion"]


def _finish(app):
    """Replaces the ordinary level-complete screen with a graded report card."""
    import tkinter as tk
    from .. import theme as T
    from .. import ui

    res = list(app.results)
    total = len(STAGE_NAMES)
    marks = []
    for i in range(total):
        rec = res[i] if i < len(res) else None
        if rec is None:
            marks.append(("not reached", 0.0, T.INK_DIM))
        elif rec[2]:
            marks.append(("shown to you", 0.35, T.WARN))
        elif rec[1] == 0:
            marks.append(("first try", 1.0, T.GOOD))
        elif rec[1] == 1:
            marks.append(("second try", 0.8, T.GOOD))
        else:
            marks.append((f"{rec[1] + 1} tries", 0.6, T.WARN))
    score = sum(m[1] for m in marks) / total

    app.progress.boss_done = True
    app.progress.boss_score = max(app.progress.boss_score, score)
    app.progress.xp += 60
    app.progress.save()
    app._refresh_hud(animate=True)

    app.content.clear()
    app.clear_actions()
    app.wrapreg.items = [(app.npc_text, 190)]
    c = app.content.inner

    grade = ("Distinction" if score >= 0.9 else "Strong pass" if score >= 0.75
             else "Pass" if score >= 0.55 else "Completed")
    head = ui.card(c, accent=T.WARN)
    tk.Label(head, text="◆", bg=T.PANEL, fg=T.WARN,
             font=(T.F_TITLE[0], 30, "bold")).pack(anchor="w")
    ui.card_title(head, f"Boss cleared — {grade}", colour=T.WARN,
                  kicker="the open question")
    ui.body_text(head,
                 f"You scored {score*100:.0f}% across the seven stages. More to the "
                 "point: you took a dataset you had never seen, chose a test nobody "
                 "told you to choose, and wrote an answer a non-statistician could "
                 "act on. That is the whole skill this course is testing.", app.wrapreg)

    card = ui.card(c, accent=T.ACCENT)
    ui.card_title(card, "Your report card", kicker="stage by stage")
    for i, name in enumerate(STAGE_NAMES):
        label, val, col = marks[i]
        row = tk.Frame(card, bg=T.PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=("✓" if val >= 0.8 else "•" if val > 0 else "—"),
                 bg=T.PANEL, fg=col, font=T.F_H2, width=3).pack(side="left")
        tk.Label(row, text=f"{i + 1}. {name}", bg=T.PANEL, fg=T.INK, font=T.F_BODY,
                 anchor="w", width=26).pack(side="left")
        tk.Label(row, text=label, bg=T.PANEL, fg=col, font=T.F_SMALL,
                 anchor="w").pack(side="left")

    r = test()
    box = ui.card(c, accent=T.GOOD)
    ui.card_title(box, "The full answer, for your notes", colour=T.GOOD,
                  kicker="model solution")
    ui.console(box,
               'data(iris)\n'
               f'tapply(iris${COL}, iris$Species, mean)\n'
               f'boxplot({COL} ~ Species, data = iris)\n'
               f't.test({COL} ~ Species, data = iris, subset = Species != "setosa")',
               r["text"].strip("\n"))
    ui.body_text(box,
                 (f"At the 5% significance level there is significant evidence that "
                  f"mean sepal width differs between {A} and {B}, with {B} averaging "
                  f"about {abs(groups()[1].mean() - groups()[0].mean()):.2f} cm wider."
                  if r["p"] < 0.05 else
                  f"At the 5% significance level there is not enough evidence that "
                  f"mean sepal width differs between {A} and {B}."),
                 app.wrapreg, fg=T.GOOD, pad=(10, 0))

    nxt = ui.card(c, accent=T.INK_DIM, bg=T.PANEL_ALT)
    ui.card_title(nxt, "Where to go from here", colour=T.INK, kicker="after the game")
    ui.body_text(nxt,
                 "Install R and RStudio, open a script, and type the commands from "
                 "this game against the real chol.txt. Every command you saw here is "
                 "the genuine article — nothing was simplified for the game. Replay "
                 "any level from the map on the left whenever a lab reminds you of it.",
                 app.wrapreg)

    app.primary("Back to menu", app.show_home)
    app.secondary("Replay the boss", app.start_boss)
    app._enter_action = app.show_home
    app.say(f"{grade}. Genuinely well done — that was the hard one, and there was "
            "nobody holding the map.", "cheer")
    app.lbl_where.configure(text="Boss cleared")
    app._refresh_hud()
    app._stagger()
