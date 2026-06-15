@echo off
cd /d "%~dp0"
call npx cap sync android
call npx cap open android
pause
