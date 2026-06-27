@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting JSP Scheduling Agent...
echo ================================
"D:\dev\python\python.exe" gui/app.py
echo ================================
echo Exit code: %errorlevel%
pause