#!/usr/bin/env bash
# Double-click this on macOS, or run ./play-mac-linux.command in a terminal.
cd "$(dirname "$0")" || exit 1

echo
echo "  ============================================"
echo "    R QUEST  -  STAT 2500"
echo "    A statistics course you play"
echo "  ============================================"
echo

PY=""
for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done

if [ -z "$PY" ]; then
    echo "  PYTHON IS NOT INSTALLED."
    echo
    echo "  macOS : install it from https://www.python.org/downloads/"
    echo "  Linux : sudo apt install python3 python3-pip python3-tk"
    echo
    read -r -p "  Press Enter to close. " _
    exit 1
fi

echo "  Found $PY. Checking the two packages it needs..."
if ! "$PY" -c "import pandas, matplotlib" >/dev/null 2>&1; then
    echo
    echo "  First run - installing pandas and matplotlib."
    echo "  This takes a minute or two. You only ever see this once."
    echo
    if ! "$PY" -m pip install --disable-pip-version-check -r requirements.txt; then
        echo
        echo "  The install failed. On Debian/Ubuntu you may need:"
        echo "     sudo apt install python3-pip python3-tk"
        echo "  or, if pip refuses to touch the system Python:"
        echo "     $PY -m pip install --break-system-packages -r requirements.txt"
        echo
        read -r -p "  Press Enter to close. " _
        exit 1
    fi
fi

echo
echo "  Starting the game."
echo
"$PY" main.py || {
    echo
    echo "  The game stopped with an error - the message above says why."
    read -r -p "  Press Enter to close. " _
    exit 1
}
