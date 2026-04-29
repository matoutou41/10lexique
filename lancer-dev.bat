@echo off
REM Lance Claude Correcteur en mode developpement (avec console pour voir les erreurs)
REM Necessite que install soit deja fait via build.bat

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Environnement non trouve. Lancez d'abord build.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python src\main.py
pause
