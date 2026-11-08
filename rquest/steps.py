"""The step model.

A level is nothing more than a list of steps.  The engine (app.py) knows how
to render each step type; level modules only describe *content*.  Adding a new
kind of teaching beat means adding one dataclass here and one render method in
the engine -- level files never need to know about Tkinter.

Step types
----------
Say        NPC speaks.  Short -- 2-4 sentences.
Explain    Plain-language concept panel, shown BEFORE any code.
Show       A real matplotlib visual of the concept.
RDemo      "Watch me do it": the exact R command plus its real output.
AskText    "Your turn": player types an R command / value.
AskChoice  "Your turn": player picks from options, each with its own diagnosis.
Recap      End-of-level takeaways pop-up.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple, Union

Text = Union[str, Callable[[], str]]


def resolve(value: Text) -> str:
    """Content may be a plain string or a zero-arg callable.

    Callables let a level defer work until the player actually reaches the
    step, so numbers shown on screen come from the dataset that really
    loaded rather than from something hard-coded at import time.
    """
    return value() if callable(value) else value


@dataclass
class Say:
    text: Text
    mood: str = "talk"          # talk | happy | think | cheer


@dataclass
class Explain:
    title: str
    body: Text
    # {jargon term: ordinary-language meaning} -- rendered as a glossary strip
    # under the body.  Every technical word gets translated on first use.
    terms: dict = field(default_factory=dict)


@dataclass
class Show:
    title: str
    caption: Text
    draw: Callable          # draw(fig) -> None, receives a matplotlib Figure
    tall: bool = False      # give the figure extra vertical room


@dataclass
class RDemo:
    title: str
    r_code: Text            # the REAL R command, shown verbatim on screen
    output: Text            # what R prints, computed from live data
    note: Text = ""         # one line on why this command, not just what


@dataclass
class AskText:
    prompt: Text
    answers: List[str]              # accepted forms; "re:" prefix = regex
    success: Text                   # why it worked
    context: Text = ""              # setup shown above the input box
    hint: Text = ""
    placeholder: str = ""
    # (regex, diagnosis) pairs tried in order against the player's raw answer.
    # This is what turns "incorrect" into "you used X, which does Y instead".
    diagnoses: List[Tuple[str, str]] = field(default_factory=list)
    # (expected, tolerance), or a callable returning that pair
    numeric: Optional[object] = None
    # Plain-English answers graded generously on keywords rather than exactly:
    #   {"must": [[synonyms], ...], "nice": [...], "avoid": [(phrase, why)],
    #    "pass": 0.75, "model": "an example of a full-credit answer"}
    free: Optional[dict] = None
    xp: int = 10


@dataclass
class AskChoice:
    prompt: Text
    options: List[str]
    correct: int
    feedback: List[Text]            # one diagnosis per option
    context: Text = ""
    success: Text = ""
    xp: int = 10


@dataclass
class Recap:
    bullets: List[Text]
    title: str = "Level recap"


@dataclass
class Level:
    number: int
    title: str
    subtitle: str
    steps: List[object]
    goal: str = ""                  # one line: what you can do after this level
    kicker: str = "LEVEL"           # what the step header calls this run
    # Set to override the normal level-complete screen (the boss uses this).
    on_finish: Optional[Callable] = None
