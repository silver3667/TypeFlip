@echo off
REM Launch the layout-fix-daemon (buffer-based, hotkey CTRL+;).
REM Double-click, or drop a shortcut into shell:startup for autostart.

setlocal
cd /d "%~dp0"

where pythonw >nul 2>nul
if %ERRORLEVEL%==0 (
    start "" pythonw run_daemon.py
) else (
    start "" python run_daemon.py
)

endlocal
