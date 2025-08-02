@echo off
echo Starting Jarvis GUI via unified entry point...
cd /d "%~dp0\.."
python main.py --gui
pause