@echo off
title R Quest - STAT 2500
cd /d "%~dp0"

echo.
echo   ============================================
echo     R QUEST  -  STAT 2500
echo     A statistics course you play
echo   ============================================
echo.

rem ---- find a Python we can use -------------------------------------------
set "PY="
where py >nul 2>&1
if not errorlevel 1 set "PY=py"
if defined PY goto gotpython
where python >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto gotpython
goto nopython

:gotpython
echo   Found Python. Checking the two packages it needs...
%PY% -c "import pandas, matplotlib" >nul 2>&1
if not errorlevel 1 goto play

echo.
echo   First run - installing pandas and matplotlib.
echo   This takes a minute or two. You only ever see this once.
echo.
%PY% -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto pipfail

:play
echo.
echo   Starting the game. You can close this black window when you finish.
echo.
%PY% main.py
if errorlevel 1 goto runfail
exit /b 0

rem ---- things that can go wrong -------------------------------------------
:nopython
echo.
echo   PYTHON IS NOT INSTALLED (or Windows cannot find it).
echo.
echo   1. Go to  https://www.python.org/downloads/
echo   2. Download and run the installer.
echo   3. IMPORTANT: on the very first screen, tick the box that says
echo      "Add python.exe to PATH" before you click Install.
echo   4. Restart your computer, then double-click this file again.
echo.
pause
exit /b 1

:pipfail
echo.
echo   The package install failed.
echo   The usual cause is no internet connection, or a school/work network
echo   blocking it. Try again on a normal connection.
echo.
pause
exit /b 1

:runfail
echo.
echo   The game stopped with an error. The message above this line says why.
echo   Copy it and open an issue on the GitHub page - that is genuinely useful.
echo.
pause
exit /b 1
