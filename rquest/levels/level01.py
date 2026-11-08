"""LEVEL 1 - Getting data into R, and drawing categorical data.

Covers: c(), the assignment arrow, printing, read.table()/read.csv() from a
URL and from a local file, table() for counting, and bar / pie / Pareto charts.
Assumes the player has never written a line of code in their life.
"""

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R
from ._common import (data, frame, offline_notice, counts_of,
                      DIAG_MEAN_FOR_TABLE, DIAG_SUMMARY_FOR_TABLE,
                      DIAG_PLOT_RAW_CATEGORY, DIAG_EQUALS_COMPARISON)

KEY = "chol"


def _smoke():
    return counts_of(KEY, "SMOKE")


def _blood():
    return counts_of(KEY, "BLOOD")


def _pareto_output():
    """What the sort / cumsum steps actually print in the R console."""
    labs, cnt = _smoke()
    pairs = sorted(zip(labs, cnt), key=lambda p: -p[1])
    labs = [p[0] for p in pairs]
    cnt = [p[1] for p in pairs]
    total = sum(cnt)
    run, cum = 0, []
    for c in cnt:
        run += c
        cum.append(round(100 * run / total, 1))
    return ("> counts\n" + R.format_named(labs, [str(c) for c in cnt]) +
            "\n\n> cumulative\n" +
            R.format_named(labs, [f"{v:.1f}" for v in cum]))


def build():
    return Level(
        number=1,
        title="Getting data into R",
        subtitle="Vectors, reading files, counting categories, and three charts",
        goal="You can now load a real dataset from the internet, count how often each "
             "category appears, and draw the three charts the lab asks for.",
        steps=[

Say("Welcome to the lab. I am Professor Byte, and for the next few hours I am your "
    "TA. We begin at the very beginning: I will not assume you know what a variable "
    "is, let alone a dataset.", "happy"),

Explain(
    "What R actually is",
    "R is a calculator that remembers things. You type an instruction, press Enter, "
    "and R does it immediately and prints the answer.\n\n"
    "The two things you do constantly in R are: put something in a labelled box so "
    "you can use it later, and call a ready-made tool by name to do a job for you. "
    "That is genuinely the whole idea. Everything else in this course is which tool "
    "to call and when.",
    {
        "variable": "a labelled box you put a value in, so you can use it by name later",
        "function": "a ready-made tool. You write its name, then brackets, and inside "
                    "the brackets you put what you want it to work on",
        "argument": "whatever you put inside a function's brackets",
    }),

RDemo("Putting things in boxes, and lining values up in a row",
      'age <- 20\nage\n\nages <- c(20, 53, 44, 37)\nages',
      "[1] 20\n\n[1] 20 53 44 37",
      "The arrow <- means 'put the thing on the right into the box on the left'. "
      "It points at the box. Typing the box's name on its own prints what is inside.\n\n"
      "c() is short for 'combine'. It glues several values into one row of values, "
      "which R calls a VECTOR. The [1] at the start of the output is just R telling "
      "you that the line begins with item number 1 — it is not part of your data."),

AskText(
    prompt="Store the four numbers 12, 7, 19 and 4 in a box called scores.",
    context="You are starting from an empty R session. Nothing exists yet.",
    answers=["scores <- c(12, 7, 19, 4)", "scores = c(12, 7, 19, 4)",
             "re:scores=c\\(12,7,19,4\\)"],
    placeholder="name <- c(value, value, ...)",
    hint="Two pieces: the arrow <- puts something into a name, and c() combines "
         "several values into one row. You need both.",
    success="That is the pattern you will use all term: a name, the arrow, and c() "
            "holding the values separated by commas.",
    diagnoses=[
        (r"c\s*\(\s*12\s+7", "Your values are separated by spaces. R needs commas "
                             "between them: c(12, 7, 19, 4)."),
        (r"scores\s*(<-|=)\s*12\s*,", "You left out c(). Without it R sees four "
                                      "separate things and does not know you meant one "
                                      "row of values. Wrap them: c(12, 7, 19, 4)."),
        (r"^\s*c\s*\(", "You built the vector but never gave it a name, so R prints it "
                        "and forgets it. Put scores <- in front."),
        DIAG_EQUALS_COMPARISON,
        (r"vector\s*\(", "vector() makes an EMPTY vector of a given length. To combine "
                         "values you already have, the function is c()."),
    ]),

Explain(
    "A dataset is a table",
    "Real data does not arrive as four numbers. It arrives as a table: one row per "
    "thing you measured, one column per thing you measured about it.\n\n"
    "This course's dataset has 300 rows — 300 adults — and seven columns: their age, "
    "height, weight, cholesterol reading, smoking habit, blood group and whether they "
    "were alive at follow-up. R calls this shape a DATA FRAME.",
    {
        "data frame": "R's word for a table of data: rows are cases, columns are variables",
        "row": "one case — here, one person",
        "column": "one thing measured about every case — here, everyone's age",
    }),

RDemo("Reading a file straight off the internet",
      lambda: data(KEY).r_command,
      lambda: offline_notice(KEY) + "\n\n" + data(KEY).r_head(6),
      lambda:
      "read.table() opens a file and hands back a data frame. header = TRUE tells R "
      "that the first line of the file is the column NAMES, not data — leave it out "
      "and R would treat the word AGE as somebody's age.\n\n"
      "The file lives at a web address, and R will happily read a URL as if it were "
      "on your hard drive. For a file on your own computer you pass a path instead:\n\n"
      "    chol <- read.table(\"C:/Users/you/Desktop/chol.txt\", header = TRUE)\n\n"
      "Note the forward slashes, even on Windows."),

AskChoice(
    prompt="Your classmate has a file called sales.csv where the values are separated "
           "by commas, and the first line holds the column names. Which line reads it?",
    options=[
        'read.csv("sales.csv")',
        'read.csv("sales.csv", header = FALSE)',
        'read.table("sales.csv")',
        'read("sales.csv")',
    ],
    correct=0,
    feedback=[
        "read.csv() is the comma-separated version of read.table(), and it already "
        "assumes header = TRUE and sep = \",\" — which is exactly this file.",
        "header = FALSE tells R the first line is data. It would turn your column "
        "names into a row of values and name the columns V1, V2, V3 instead.",
        "read.table() defaults to splitting on SPACES, not commas. On a comma file it "
        "would read each whole line as a single column. You would need "
        "read.table(\"sales.csv\", sep = \",\", header = TRUE).",
        "There is no function called read() in base R. The family is read.table(), "
        "read.csv() and friends — the part after the dot says what kind of file.",
    ],
    success="read.csv() is read.table() with the comma-file settings already filled in."),

Explain(
    "Two kinds of column, two kinds of question",
    "Some columns hold NUMBERS you can do arithmetic on: age, weight, cholesterol. "
    "Others hold LABELS: smoking habit, blood group, alive or dead. Averaging a label "
    "is meaningless — there is no average of 'pipe' and 'nonsmo'.\n\n"
    "So for label columns the first question is always the same: how many of each? "
    "The function that answers it is table().",
    {
        "numeric variable": "a column of numbers that arithmetic makes sense on",
        "categorical variable": "a column of labels or groups. You count these, you do "
                                "not average them",
        "frequency": "how many times something appeared — a count",
    }),

RDemo("Counting the categories",
      "table(chol$SMOKE)",
      lambda: R.format_table(frame(KEY)["SMOKE"]),
      "The $ picks one column out of the data frame: chol$SMOKE means 'the SMOKE "
      "column of the chol table'. table() then counts how many times each distinct "
      "label appears, and prints the labels above their counts.\n\n"
      "This little table is what every categorical chart is built from."),

AskText(
    prompt="Now count the blood groups. The column is called BLOOD and the data frame "
           "is called chol.",
    answers=["table(chol$BLOOD)"],
    placeholder="function(dataframe$COLUMN)",
    hint="Same shape as the command I just ran, with a different column name after "
         "the dollar sign.",
    success=lambda: "That gives:\n\n" + R.format_table(frame(KEY)["BLOOD"]) +
                    "\n\nCounts for every distinct label, with no extra work from you.",
    diagnoses=[
        (r"table\s*\(\s*BLOOD\s*\)",
         "R does not know what BLOOD is on its own — it only exists inside the chol "
         "table. You have to say which table it came from: chol$BLOOD."),
        (r"table\s*\(\s*chol\s*\)",
         "That hands table() the entire data frame, so R tries to cross-tabulate all "
         "seven columns at once. Point it at the single column you want: chol$BLOOD."),
        (r"chol\.BLOOD|chol\[BLOOD\]",
         "The separator between a data frame and one of its columns is the dollar "
         "sign: chol$BLOOD."),
        DIAG_MEAN_FOR_TABLE,
        DIAG_SUMMARY_FOR_TABLE,
    ]),

Show("The bar plot: counts as heights",
     lambda: "Three smoking categories, drawn as three bars. The height of a bar IS "
             "the count from table() — nothing more clever than that. Bar charts are "
             "the default choice for categorical data because comparing heights is "
             "something the human eye does extremely well.",
     lambda fig: P.barplot(fig, *_smoke(), title="barplot(table(chol$SMOKE))",
                           xlabel="smoking habit")),

RDemo("Drawing it",
      'barplot(table(chol$SMOKE),\n        main = "Smoking habits",\n'
      '        xlab = "habit", ylab = "number of people",\n'
      '        col = "steelblue")',
      "(a plot window opens)",
      "Read it from the inside out: table() counts, and barplot() draws whatever it "
      "is handed. R lets you nest functions like this, and it is the normal way to "
      "write R.\n\n"
      "main = is the title, xlab = and ylab = are the axis labels, col = is the "
      "colour. Arguments with names like these are optional — leave them out and R "
      "picks something plain."),

AskText(
    prompt="Draw a bar plot of the blood groups. Do it in one line, without storing "
           "anything in between.",
    answers=["barplot(table(chol$BLOOD))",
             "re:barplot\\(table\\(chol\\$blood\\)(,.*)?\\)"],
    placeholder="barplot(...)",
    hint="Nest them: the counting function goes INSIDE the drawing function's brackets.",
    success="Nesting like this — barplot(table(x)) — is the single most common pattern "
            "in the categorical part of this course.",
    diagnoses=[
        DIAG_PLOT_RAW_CATEGORY,
        (r"table\s*\(\s*barplot",
         "You have them the wrong way round. The counting has to happen first, so "
         "table() goes on the inside: barplot(table(chol$BLOOD))."),
        (r"^\s*table\s*\(",
         "That counts them but never draws anything. Wrap the whole thing in "
         "barplot( ... )."),
        (r"\bplot\s*\(", "plot() is the general-purpose plotter and on a table it "
                         "would draw dots joined up. For categorical counts you want "
                         "bars: barplot()."),
    ]),

Show("The pie chart: counts as slices",
     "Same three numbers, drawn as shares of a whole. A pie answers 'what fraction "
     "of the group?' rather than 'how many?'. It works with a handful of categories "
     "and becomes unreadable beyond about five, because judging angles is much harder "
     "than judging heights.",
     lambda fig: P.piechart(fig, *_smoke(), title="pie(table(chol$SMOKE))")),

RDemo("The pie command",
      'pie(table(chol$SMOKE), main = "Share of each smoking habit")',
      "(a plot window opens)",
      "Identical structure to barplot — count first, draw second. R's pie() takes the "
      "same table object."),

Show("The Pareto diagram: sorted bars plus a running total",
     lambda: "A Pareto diagram is a bar chart with two rules added: the bars are "
             "sorted tallest first, and a line tracks the running cumulative "
             "percentage. It answers a question the other two cannot — 'how few "
             "categories do I need before I have covered most of the cases?' Here the "
             "biggest category alone already accounts for the height of the first "
             "point on the orange line.",
     lambda fig: P.pareto(fig, *_smoke(),
                          title="Pareto diagram of smoking habits"),
     tall=True),

RDemo("Building a Pareto diagram in R",
      'counts <- table(chol$SMOKE)\n'
      'counts <- sort(counts, decreasing = TRUE)\n'
      'barplot(counts, main = "Pareto diagram")\n'
      'cumulative <- cumsum(counts) / sum(counts) * 100\n'
      'lines(cumulative)',
      lambda: _pareto_output(),
      "There is no single pareto() function in base R — you build it from pieces you "
      "already know. sort(..., decreasing = TRUE) puts the tallest bar first, cumsum() "
      "adds the counts up as it goes along, and dividing by the total turns that "
      "running sum into a running percentage."),

AskChoice(
    prompt="A shop logs 1,400 customer complaints across 9 categories and wants to "
           "know which few problems to fix first. Which chart?",
    options=[
        "A Pareto diagram",
        "A pie chart",
        "A plain bar plot in alphabetical order",
        "A histogram",
    ],
    correct=0,
    feedback=[
        "Right — sorted bars show the worst offenders immediately, and the cumulative "
        "line tells you exactly how many categories you must fix to cover, say, 80% "
        "of complaints. That is the question being asked.",
        "Nine slices is too many to read, and a pie gives no sense of running total, "
        "so it cannot answer 'how few do I need to fix?'.",
        "A plain bar plot shows the counts but alphabetical order scatters the big "
        "categories randomly across the chart, and there is no cumulative line.",
        "A histogram is for NUMERIC data — it slices a number line into bins. "
        "Complaint categories are labels, so there is no number line to slice.",
    ],
    success="Pareto is the 'which few things matter most' chart."),

Recap(bullets=[
    "<- puts a value into a named box; c() combines several values into one vector; "
    "typing a name prints what is in it.",
    "read.table(file, header = TRUE) and read.csv(file) turn a file into a data "
    "frame, and the file may be a URL or a path on your own machine.",
    "$ picks one column out of a data frame: chol$SMOKE.",
    "table() counts a categorical column. Every categorical chart is drawn from that "
    "table, not from the raw column.",
    "barplot() for comparing counts, pie() for shares of a whole, and a sorted "
    "barplot plus a cumsum() line for a Pareto when you need to know which few "
    "categories dominate.",
]),
        ])
