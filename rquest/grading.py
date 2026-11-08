"""Answer checking with *diagnostic* feedback.

The design rule for this game is that a wrong answer must never come back as
just "incorrect".  Every AskText step carries a list of (regex, diagnosis)
pairs describing the mistakes a beginner actually makes, and this module runs
them in order so the player is told what their command WOULD have done.
"""

import re

# Things a beginner types that mean the same thing as the model answer.
_QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def normalise(s: str) -> str:
    """Reduce an R command to a canonical form for comparison.

    Forgives: capitalisation, spacing, single vs double quotes, a trailing
    semicolon, `=` vs `<-` for assignment, and `T`/`F` for `TRUE`/`FALSE`.
    Does NOT forgive anything that changes what the command actually does.
    """
    s = (s or "").translate(_QUOTES).strip()
    s = s.rstrip(";").strip()
    s = s.replace("<-", "=")                # assignment forms are equivalent
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([(),=\[\]$~+*/^])\s*", r"\1", s)
    s = s.replace("'", '"')
    s = s.lower()
    s = re.sub(r"\btrue\b", "t", s)
    s = re.sub(r"\bfalse\b", "f", s)
    return s


def _as_number(s: str):
    """Pull a single number out of a free-text answer, if there is one."""
    s = (s or "").strip().replace(",", "")
    m = re.fullmatch(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?%?", s)
    if not m:
        # allow things like "p = 0.0342" or "about 0.34"
        nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
        if len(nums) != 1:
            return None
        s = nums[0]
    pct = s.endswith("%")
    try:
        v = float(s.rstrip("%"))
    except ValueError:
        return None
    return v / 100.0 if pct else v


def check(answer: str, step) -> tuple:
    """Grade one answer.

    Returns (ok, message).  When ok is False the message is the most specific
    diagnosis we can offer, falling back to the step's hint.
    """
    raw = (answer or "").strip()
    if not raw:
        return False, "Nothing typed yet -- have a go, a wrong answer here costs you nothing."

    # --- plain-English questions -------------------------------------------
    spec_free = getattr(step, "free", None)
    if callable(spec_free):
        spec_free = spec_free()
    if spec_free:
        if len(raw.split()) < 4:
            return False, ("That is too short to be a conclusion. Write it as a full "
                           "sentence someone outside this course could understand.")
        score, notes = grade_free_text(raw, spec_free["must"],
                                       spec_free.get("nice", ()),
                                       spec_free.get("avoid", ()))
        if score >= spec_free.get("pass", 0.75):
            return True, ""
        msg = ["Your sentence is missing something a marker would look for."]
        for n in notes:
            if n.startswith("missing: "):
                msg.append(f"  - no mention of {n[9:]}")
            else:
                msg.append(f"  - {n}")
        msg.append("\nA full-credit answer reads something like:\n\n    "
                   + spec_free.get("model", ""))
        return False, "\n".join(msg)

    # --- numeric questions -------------------------------------------------
    spec = getattr(step, "numeric", None)
    if callable(spec):
        spec = spec()
    if spec:
        expected, tol = spec
        got = _as_number(raw)
        if got is None:
            return False, ("I could not find a single number in that. Type just the "
                           "value, for example 0.2461 -- no command, no units.")
        if abs(got - expected) <= tol:
            return True, ""
        # near-miss diagnostics that catch the classic slips
        if abs(got - expected) <= tol * 12:
            return False, (f"Very close. You gave {got:g}, I am looking for something "
                           f"nearer {expected:g}. Check your rounding and make sure you "
                           f"copied every digit R printed.")
        if abs((1 - got) - expected) <= tol * 3:
            return False, (f"You have computed the *opposite* tail. {got:g} is the "
                           f"complement of the answer -- remember P(X > k) = 1 - P(X <= k), "
                           f"so subtract from 1 exactly once, not zero or twice.")
        for rx, msg in getattr(step, "diagnoses", []):
            if re.search(rx, raw, re.I):
                return False, msg
        return False, step.hint or f"Not quite -- have another look at the numbers."

    # --- command questions -------------------------------------------------
    norm = normalise(raw)
    for a in step.answers:
        if a.startswith("re:"):
            if re.fullmatch(a[3:], norm):
                return True, ""
        elif normalise(a) == norm:
            return True, ""

    for rx, msg in getattr(step, "diagnoses", []):
        if re.search(rx, raw, re.I):
            return False, msg

    return False, _generic_diagnosis(raw, step)


def _generic_diagnosis(raw: str, step) -> str:
    """Last-resort feedback that still says something useful."""
    model = step.answers[0] if step.answers else ""
    opens, closes = raw.count("("), raw.count(")")
    if opens != closes:
        return (f"Your brackets do not balance -- {opens} opening, {closes} closing. "
                "R will just sit there waiting for the rest of the command.")
    if opens == 0 and "(" in model:
        fn = model.split("(")[0]
        return (f"That has no brackets in it. In R you *call* a function by putting "
                f"brackets after its name, like {fn}(...). Without them R just shows "
                f"you the function's own code.")
    if "=" in raw and "==" not in raw and "<-" not in raw and "(" not in raw:
        return ("Looks like an assignment. Assignment stores something for later; "
                "here I want the command that produces the answer now.")
    fn_typed = re.match(r"\s*([A-Za-z_.][\w.]*)\s*\(", raw)
    fn_model = re.match(r"\s*([A-Za-z_.][\w.]*)\s*\(", model)
    if fn_typed and fn_model and fn_typed.group(1).lower() != fn_model.group(1).lower():
        return (f"You reached for {fn_typed.group(1)}(). That is a real function, but it "
                f"answers a different question than the one I asked. "
                + (step.hint or f"Think about which function reports this."))
    return step.hint or ("Not the command I am after. Re-read the question and think "
                         "about which single function does that job.")


def grade_free_text(answer: str, must_have, nice_to_have=(), forbidden=()):
    """Generous keyword grading for plain-English conclusions (boss challenge).

    must_have    : list of groups; each group is a list of synonyms, and the
                   answer must contain at least one word from every group.
    nice_to_have : extra credit groups.
    forbidden    : phrases that indicate a real misinterpretation.
    Returns (score 0..1, list of notes).
    """
    low = " " + re.sub(r"\s+", " ", (answer or "").lower()) + " "
    notes, hits = [], 0
    for group in must_have:
        if any(w.lower() in low for w in group):
            hits += 1
        else:
            notes.append(f"missing: {group[0]}")
    bonus = sum(1 for g in nice_to_have if any(w.lower() in low for w in g))
    for phrase, why in forbidden:
        if phrase.lower() in low:
            notes.append(f"careful: {why}")
            hits = max(0, hits - 1)
    base = hits / max(1, len(must_have))
    score = min(1.0, base + 0.08 * bonus)
    return score, notes
