"""LEVEL 3 - Discrete probability distributions.

Covers: the mean and variance of a discrete random variable by hand and in R,
the binomial (dbinom exact, pbinom cumulative), translating "at least / at most
/ between" into R, the Poisson (dpois, ppois), and plotting a distribution's
shape with plot(x, y, type = "h").
"""

import numpy as np

from ..steps import Level, Say, Explain, Show, RDemo, AskText, AskChoice, Recap
from .. import plots as P
from .. import rstats as R

# A small claims example with deliberately tidy numbers, so the player can
# check the arithmetic by hand and see it land exactly on R's answer.
XS = [0, 1, 2, 3]
PS = [0.4, 0.3, 0.2, 0.1]

N_PAT, P_RESP = 12, 0.25        # binomial scenario
LAM = 3.5                       # Poisson scenario


def _mu_var():
    return R.discrete_mean_var(XS, PS)


def build():
    mu, v = _mu_var()
    return Level(
        number=3,
        title="Discrete distributions",
        subtitle="Random variables, the binomial and the Poisson",
        goal="You can now compute the mean and variance of a discrete random "
             "variable, and answer any 'exactly / at most / at least / between' "
             "question with dbinom, pbinom, dpois and ppois.",
        steps=[

Say("So far everything has been data you already had. Now we go the other way: "
    "before collecting anything, what does chance say SHOULD happen? That is what a "
    "probability distribution is for.", "talk"),

Explain(
    "Random variable, and its distribution",
    "A RANDOM VARIABLE is just a number whose value depends on chance — the number of "
    "claims an insurer gets tomorrow, the number of patients who respond to a drug. "
    "We write it with a capital letter, X.\n\n"
    "Its DISTRIBUTION is the full list of values it could take and the probability of "
    "each. Because it is a full list of every possibility, the probabilities always "
    "add up to exactly 1. DISCRETE means the values are separate, countable things: "
    "0, 1, 2, 3 claims. You cannot have 1.4 claims.",
    {
        "random variable": "a number decided by chance, written X",
        "distribution": "the list of possible values with the probability of each",
        "discrete": "the values are separate whole things you can count, not a "
                    "continuous scale",
        "P(X = 2)": "read aloud as 'the probability that X turns out to be 2'",
    }),

Show("A discrete distribution, drawn",
     "Four possible values, four probabilities, and the bar heights add to 1. That is "
     "the entire distribution — there is nothing else to know about this random "
     "variable.",
     lambda fig: P.discrete_dist(fig, XS, PS,
                                 title="Claims received per day",
                                 xlabel="x = number of claims", ylabel="P(X = x)")),

Explain(
    "The mean and variance of a random variable",
    "For DATA you add up the values and divide. For a random variable there is no "
    "data yet, so instead you weight each possible value by how likely it is:\n\n"
    "    mean  =  sum of  x times P(X = x)\n"
    "    var   =  sum of  x squared times P(X = x)   minus   mean squared\n\n"
    "The mean is also called the EXPECTED VALUE. Do not read too much into the name: "
    "it is the long-run average, and it need not be a value X can actually take. A "
    "mean of 1.4 claims a day is perfectly sensible even though no day has 1.4 claims.",
    {
        "expected value, E(X)": "the long-run average value of the random variable",
        "weighting": "multiplying each value by its probability, so likely values "
                     "count for more",
    }),

RDemo("Doing it in R",
      'x <- c(0, 1, 2, 3)\n'
      'p <- c(0.4, 0.3, 0.2, 0.1)\n\n'
      'mu <- sum(x * p)\nmu\n\n'
      'variance <- sum(x^2 * p) - mu^2\nvariance',
      lambda: f"[1] {R.sig(mu, 6)}\n\n[1] {R.sig(v, 6)}",
      "x * p multiplies the two vectors position by position — first with first, "
      "second with second — and sum() adds the results. That one line IS the formula.\n\n"
      "Notice R never needed a loop. Working on whole vectors at once is R's "
      "personality, and it is why statistical formulas translate so directly."),

AskText(
    prompt="A different variable Y takes the values 1, 2 and 3 with probabilities "
           "0.5, 0.3 and 0.2. What is E(Y)? Give the number.",
    context="y <- c(1, 2, 3)\np <- c(0.5, 0.3, 0.2)",
    answers=[],
    numeric=(1.7, 0.005),
    placeholder="a number",
    hint="Multiply each value by its own probability, then add the three results "
         "together: 1(0.5) + 2(0.3) + 3(0.2).",
    success="1(0.5) + 2(0.3) + 3(0.2) = 0.5 + 0.6 + 0.6 = 1.7. In R that is "
            "sum(y * p), and note again that 1.7 is not a value Y can ever take.",
    diagnoses=[
        (r"^\s*2\s*$", "2 is the middle VALUE, not the expected value. The three "
                       "outcomes are not equally likely, so you cannot just take the "
                       "middle one — each has to be weighted by its probability."),
        (r"^\s*6\s*$", "You added the values 1 + 2 + 3 and forgot to weight them by "
                       "their probabilities."),
        (r"^\s*1\s*$", "That is the most likely single value, which is called the mode. "
                       "The expected value averages all three, weighted."),
    ]),

Explain(
    "The binomial: counting successes in a fixed number of tries",
    "Some situations come up so often that the probabilities have been worked out once "
    "and for all. The BINOMIAL is the most common: you repeat the same yes/no trial a "
    "fixed number of times and count how many come out 'yes'.\n\n"
    "It applies when all four of these hold: the number of trials n is fixed in "
    "advance; each trial is a simple success or failure; the probability p of success "
    "is the same every time; and the trials do not influence each other.",
    {
        "trial": "one attempt with a yes/no result — one patient, one coin flip",
        "n": "how many trials you run, fixed before you start",
        "p": "the probability of success on any single trial",
        "success": "whichever outcome you decided to count. It need not be a good thing",
    }),

Show("What a binomial distribution looks like",
     f"12 patients, each with a {P_RESP:.0%} chance of responding. The bars give the "
     f"probability of ending up with exactly 0, 1, 2 ... responders. The peak sits "
     f"near n times p = {N_PAT * P_RESP:g}, which is the binomial's mean.",
     lambda fig: P.discrete_dist(
         fig, list(range(N_PAT + 1)),
         [R.dbinom(k, N_PAT, P_RESP) for k in range(N_PAT + 1)],
         title=f"Binomial: n = {N_PAT}, p = {P_RESP}",
         xlabel="x = number of responders", ylabel="P(X = x)")),

RDemo("dbinom: the probability of EXACTLY k",
      f"dbinom(3, size = {N_PAT}, prob = {P_RESP})",
      lambda: f"[1] {R.sig(R.dbinom(3, N_PAT, P_RESP), 7)}",
      lambda:
      f"So there is about a {R.dbinom(3, N_PAT, P_RESP):.1%} chance that exactly 3 of "
      f"the {N_PAT} patients respond.\n\n"
      "The d stands for DENSITY, which for a discrete variable just means 'the "
      "probability of exactly this value'. size is n, prob is p. You can drop the "
      f"names and write dbinom(3, {N_PAT}, {P_RESP}) as long as you keep the order."),

AskText(
    prompt=f"What R command gives the probability that exactly 5 of the {N_PAT} "
           f"patients respond?",
    answers=[f"dbinom(5, {N_PAT}, {P_RESP})",
             f"dbinom(5, size = {N_PAT}, prob = {P_RESP})",
             f"re:dbinom\\(x?=?5,(size=)?{N_PAT},(prob=)?0\\.25\\)"],
    placeholder=f"dbinom(k, n, p)",
    hint=f"Three numbers in order: how many successes you are asking about, then n, "
         f"then p.",
    success=lambda: f"That returns {R.sig(R.dbinom(5, N_PAT, P_RESP), 6)} — about "
                    f"{R.dbinom(5, N_PAT, P_RESP):.1%}.",
    diagnoses=[
        (r"pbinom", "pbinom() is CUMULATIVE — it adds up everything from 0 up to your "
                    "number. For exactly one value you want dbinom()."),
        (r"dbinom\s*\(\s*12\s*,\s*5", "Your arguments are in the wrong order. The "
                                      "number of successes comes FIRST, then n, then p: "
                                      f"dbinom(5, {N_PAT}, {P_RESP})."),
        (r"dbinom\s*\([^,]*,[^,]*\)\s*$", "dbinom() needs three things: the value, n "
                                          "and p. You have given it two."),
        (r"rbinom", "rbinom() GENERATES random results — it simulates. You want the "
                    "exact probability, which is dbinom()."),
    ]),

Explain(
    "At most, at least, between",
    "Exam questions almost never ask for exactly one value. They ask for a range, and "
    "each phrase turns into a specific R expression:\n\n"
    "    at most k        P(X <= k)        pbinom(k, n, p)\n"
    "    fewer than k     P(X <= k-1)      pbinom(k-1, n, p)\n"
    "    at least k       P(X >= k)        1 - pbinom(k-1, n, p)\n"
    "    more than k      P(X > k)         1 - pbinom(k, n, p)\n"
    "    between a and b  P(a <= X <= b)   pbinom(b, n, p) - pbinom(a-1, n, p)\n\n"
    "Every one of those is built from pbinom, which always means 'add up everything "
    "from 0 up to and including this value'. The k-1 offsets are where marks get lost: "
    "'at least 5' includes 5, so you must subtract off everything up to 4, not up to 5.",
    {
        "cumulative": "added up from the bottom — every outcome up to and including k",
        "pbinom(k, n, p)": "P(X <= k), always 'up to and including'",
    }),

Show("Why 'at least' needs the k-1",
     f"Gold bars are the outcomes counted by 'at least 5 responders'. To get their "
     f"total you take the whole distribution (1) and subtract the blue bars, which are "
     f"0 through 4 — that is pbinom(4, ...), not pbinom(5, ...).",
     lambda fig: P.discrete_dist(
         fig, list(range(N_PAT + 1)),
         [R.dbinom(k, N_PAT, P_RESP) for k in range(N_PAT + 1)],
         title="P(X >= 5) = 1 - pbinom(4, 12, 0.25)",
         xlabel="x = number of responders", ylabel="P(X = x)",
         highlight=list(range(5, N_PAT + 1)),
         highlight_label="P(X >= 5)")),

AskChoice(
    prompt=f"Which command gives the probability that AT LEAST 5 of the {N_PAT} "
           f"patients respond?",
    options=[
        f"1 - pbinom(4, {N_PAT}, {P_RESP})",
        f"1 - pbinom(5, {N_PAT}, {P_RESP})",
        f"pbinom(5, {N_PAT}, {P_RESP})",
        f"dbinom(5, {N_PAT}, {P_RESP})",
    ],
    correct=0,
    feedback=[
        "Correct. 'At least 5' includes 5 itself, so the part you throw away is "
        "0 through 4 — pbinom(4, ...).",
        "Close, but that subtracts everything up to AND INCLUDING 5, so you have "
        "thrown away the 5 you were supposed to keep. This gives P(X >= 6).",
        "That is P(X <= 5) — at most 5, the opposite end. Subtracting it from 1 is "
        "the missing step, and even then you would need pbinom(4).",
        "dbinom gives exactly 5 and nothing above it, so it misses 6, 7, 8 ... up to "
        "12, which 'at least 5' includes.",
    ],
    success=lambda: f"It comes to {R.sig(1 - R.pbinom(4, N_PAT, P_RESP), 6)}."),

AskText(
    prompt=f"Now a number rather than a command. What is the probability that AT MOST "
           f"2 of the {N_PAT} patients respond? Use pbinom and give four decimal places.",
    context=f"n = {N_PAT} patients,  p = {P_RESP} chance each,  'at most 2'",
    answers=[],
    numeric=(R.pbinom(2, N_PAT, P_RESP), 0.0005),
    placeholder="0.xxxx",
    hint="'At most 2' is P(X <= 2), which is exactly what pbinom(2, n, p) returns — "
         "no subtracting from 1 and no k-1 adjustment this time.",
    success=lambda: f"pbinom(2, {N_PAT}, {P_RESP}) = "
                    f"{R.sig(R.pbinom(2, N_PAT, P_RESP), 6)}. 'At most' is the one "
                    "phrase that maps straight onto pbinom with no adjustment at all.",
    diagnoses=[
        (r"^\s*0?\.2581", "That is dbinom(2, 12, 0.25) — the probability of EXACTLY 2. "
                          "'At most 2' also includes 0 and 1."),
    ]),

Explain(
    "The Poisson: counts with no fixed maximum",
    "The binomial needs a fixed number of trials. But how many trials are there in "
    "'phone calls arriving at a help desk in an hour'? There is no n — a call either "
    "happens or it does not, at any instant.\n\n"
    "For counts of events in a fixed window of time or space, the POISSON distribution "
    "is the right tool. It has a single parameter, lambda, the average number of events "
    "per window. Its mean and its variance are BOTH equal to lambda, which is a handy "
    "sanity check: if your count data has a variance wildly different from its mean, "
    "Poisson is probably the wrong model.",
    {
        "lambda": "the average number of events per window. The only number Poisson needs",
        "window": "the fixed stretch of time, area or volume you are counting within",
    }),

Show("Poisson shape",
     f"Calls arriving at a help desk, averaging lambda = {LAM} per hour. Counts have no "
     f"upper limit — the bars carry on to the right forever, they just get very small. "
     f"Both the mean and the variance of this distribution are {LAM}.",
     lambda fig: P.discrete_dist(
         fig, list(range(13)), [R.dpois(k, LAM) for k in range(13)],
         title=f"Poisson: lambda = {LAM}",
         xlabel="x = calls in an hour", ylabel="P(X = x)")),

RDemo("dpois and ppois behave exactly like dbinom and pbinom",
      f"dpois(2, lambda = {LAM})\nppois(2, lambda = {LAM})\n1 - ppois(5, lambda = {LAM})",
      lambda: f"[1] {R.sig(R.dpois(2, LAM), 7)}\n"
              f"[1] {R.sig(R.ppois(2, LAM), 7)}\n"
              f"[1] {R.sig(1 - R.ppois(5, LAM), 7)}",
      "Same two letters doing the same two jobs: d for exactly, p for cumulative. Only "
      "the parameters change, because Poisson needs one number where the binomial "
      "needs two.\n\n"
      "That pattern is not a coincidence, and in the next level I am going to show you "
      "that it holds for every distribution in R."),

AskText(
    prompt=f"A bakery sells on average {LAM} birthday cakes a day. Write the R command "
           f"for the probability of selling exactly 6 cakes tomorrow.",
    answers=[f"dpois(6, {LAM})", f"dpois(6, lambda = {LAM})",
             f"re:dpois\\(x?=?6,(lambda=)?3\\.5\\)"],
    placeholder="dpois(k, lambda)",
    hint="Exactly one value means the d function. Poisson takes only the count and "
         "lambda — there is no n.",
    success=lambda: f"= {R.sig(R.dpois(6, LAM), 6)}, about "
                    f"{R.dpois(6, LAM):.1%}. Note there was no n to supply; that "
                    "absence is the signature of a Poisson problem.",
    diagnoses=[
        (r"ppois", "ppois() is cumulative: it would give the probability of 6 OR FEWER. "
                   "For exactly 6 you want dpois()."),
        (r"dbinom|pbinom", "Binomial needs a fixed number of trials n. There is no "
                           "such thing as 'the number of cake-buying attempts' here — "
                           "this is a count in a time window, so it is Poisson."),
        (r"dpois\s*\(\s*3\.5\s*,\s*6", "Arguments are the wrong way round: the count "
                                       f"you are asking about comes first, then lambda: "
                                       f"dpois(6, {LAM})."),
    ]),

RDemo("Plotting a distribution's shape",
      f'x <- 0:12\ny <- dpois(x, lambda = {LAM})\n'
      'plot(x, y, type = "h", lwd = 3,\n'
      '     main = "Poisson, lambda = 3.5",\n'
      '     xlab = "calls per hour", ylab = "probability")',
      "(a plot window opens)",
      "0:12 is shorthand for the whole run of whole numbers from 0 to 12. dpois() then "
      "works on all thirteen at once and hands back thirteen probabilities.\n\n"
      'type = "h" draws each point as a vertical spike down to the axis, which is the '
      "conventional way to draw a discrete distribution — the gaps between spikes are "
      "the point, because values in between are impossible."),

Recap(bullets=[
    "A discrete random variable is described by its list of values and their "
    "probabilities; mean = sum(x * p) and variance = sum(x^2 * p) - mean^2.",
    "Binomial: a fixed number of independent yes/no trials with the same p. "
    "dbinom(k, n, p) for exactly k, pbinom(k, n, p) for k or fewer.",
    "Translate the words: at most k is pbinom(k), at least k is 1 - pbinom(k-1), "
    "between a and b is pbinom(b) - pbinom(a-1). The k-1 is where marks are lost.",
    "Poisson: counts of events in a window, one parameter lambda, which is both the "
    "mean and the variance. dpois and ppois work exactly like dbinom and pbinom.",
    'plot(x, y, type = "h") is the standard picture of a discrete distribution.',
]),
        ])
