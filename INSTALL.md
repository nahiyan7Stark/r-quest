# How to run R Quest

**You do not need to know any coding to run this.** Pick the route that matches
your situation. Route A works for almost everyone and takes about three minutes.

---

## Before anything: get Python

R Quest is a Python program, so your computer needs Python. It is free and takes
two minutes.

1. Go to **https://www.python.org/downloads/**
2. Click the big yellow **Download Python** button.
3. Run the file you just downloaded.
4. **On the very first screen, tick the box that says "Add python.exe to PATH".**
   It is at the bottom and it is easy to miss. If you skip it, Windows will not
   be able to find Python later and nothing below will work.
5. Click **Install Now**, wait, then click **Close**.
6. **Restart your computer.** Windows only notices the change after a restart.

> Already have Python? Skip to Route A.
> On **Linux** you also need `sudo apt install python3-tk` (Fedora:
> `sudo dnf install python3-tkinter`). On **macOS** and **Windows** the Python
> installer includes everything already.

---

## Route A — just double-click it (easiest)

1. Download the project and **unzip it**. Right-click the `.zip` file →
   **Extract All** → **Extract**. You must extract it; Windows will let you look
   inside a zip without extracting, and the game will not run from in there.
2. Open the extracted folder. Keep opening folders until you can see a file
   called **`main.py`** sitting next to **`Play-Windows.bat`**.
3. **Double-click `Play-Windows.bat`.**

A black window appears. The first time, it spends a minute installing two
packages — that is normal and only happens once. Then the game window opens.

You can close the black window once you have finished playing.

> ### If Windows says "Windows protected your PC"
>
> This is normal for **any** script downloaded from the internet — Windows does
> not know the file yet, so it warns about everything. Click **More info**, then
> **Run anyway**.
>
> To avoid the warning entirely, do this *before* extracting: right-click the
> downloaded `.zip` → **Properties** → tick **Unblock** at the bottom → **OK**.
> Then extract it. Windows will treat everything inside as trusted.
>
> If you would rather not run a script at all, use **Route B** below — typing
> the two commands yourself does exactly the same thing.

> **macOS / Linux:** double-click `play-mac-linux.command` instead. On macOS the
> first time you may need to right-click it → **Open** → **Open**, because macOS
> blocks downloaded scripts by default.

---

## Route B — type the commands yourself

Use this if Route A failed, or if you want to see the error messages properly.

### Step 1 — get your folder's address

Open the extracted folder in File Explorer, the one containing `main.py`.

Click once on the **address bar** at the top (the strip showing
`This PC > Downloads > ...`). It turns into editable text showing the full path,
something like:

```
I:\stats project\rquest-stat2500\rquest
```

Select it and copy it (**Ctrl+C**).

### Step 2 — open PowerShell already in that folder

Here is the trick that saves all the pain: with that folder open in File
Explorer, click the **address bar**, delete what is there, type:

```
powershell
```

and press **Enter**. A blue window opens, already pointed at that exact folder.
No typing paths at all.

### Step 3 — run these two lines

Type the first, press Enter, wait for it to finish, then type the second:

```powershell
py -m pip install -r requirements.txt
py main.py
```

### If you opened PowerShell some other way

Then you do have to tell it where to go first. Paste your copied path inside
quotes — **the quotes matter if your path has a space in it**:

```powershell
cd "I:\stats project\rquest-stat2500\rquest"
py -m pip install -r requirements.txt
py main.py
```

Check you are in the right place by typing `dir` and pressing Enter — you should
see `main.py` in the list. If you do not, there is one more folder to go into.

---

## Route C — use Thonny (no PATH, no terminal)

If Python will not install properly, or you ticked the wrong box and do not want
to redo it, **Thonny** is a beginner Python app that brings its own Python with
it. Nothing can go wrong with PATH because Thonny never uses it.

1. Install Thonny from **https://thonny.org** (free).
2. Open Thonny. Go to **Tools → Manage packages…**
3. Type `pandas` in the search box, click **Search on PyPI**, click the
   **pandas** result, then click **Install**. Wait for it to finish.
4. Do the same for `matplotlib`.
5. Close that window. Go to **File → Open…** and open `main.py` from the
   extracted folder.
6. Press the green **Run** button (or **F5**).

The game window opens. Thonny shows any error messages in the panel at the
bottom, which makes it the easiest route for reporting a problem.

---

## When something goes wrong

| What you see | What it means | Fix |
|---|---|---|
| `'py' is not recognized...` | Windows cannot find Python | You missed the **Add python.exe to PATH** tick box. Reinstall Python with it ticked, then restart. Or use Route C. |
| `'python' is not recognized...` | Same thing | Same fix. Try `py` instead of `python` first. |
| The black window flashes and vanishes | An error scrolled past too fast | Use Route B so the window stays open and you can read it. |
| `Tkinter is missing` | Python installed without its window toolkit | **Windows/macOS:** reinstall Python, making sure *tcl/tk and IDLE* is ticked. **Linux:** `sudo apt install python3-tk` |
| `No module named pandas` | The packages did not install | Run `py -m pip install -r requirements.txt` again and read what it says. |
| `pip` errors about system packages (Linux) | Your distro protects system Python | `python3 -m pip install --break-system-packages -r requirements.txt` |
| Game runs but says *OFFLINE COPY IN USE* | No internet right now | Nothing is broken. The game bundles its own copy of the data and works fully offline. |

Still stuck? **Open an issue** on the GitHub page with a copy of the error text
and what you tried. That is useful, not annoying — it tells me what to fix.

---

## What you actually need, in one line

Any Windows, Mac or Linux computer · Python 3.8 or newer · two free packages the
launcher installs for you · about 2–4 hours to finish the game.

**You do not need R installed.** The game runs the statistics itself and shows
you the exact R command for every single thing it does, so you are still
learning the R your course expects you to write.
