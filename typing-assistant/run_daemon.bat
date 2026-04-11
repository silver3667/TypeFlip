@echo off
REM Launch the typing-assistant daemon in the background (no console window).
REM Double-click this file, or drop a shortcut to it into shell:startup for autostart.

setlocal
cd /d "%~dp0"

REM Prefer pythonw.exe so no console window is shown. Fallback to python.exe.
where pythonw >nul 2>nul
if %ERRORLEVEL%==0 (
    start "" pythonw run_daemon.py
) else (
    start "" python run_daemon.py
)

endlocal
