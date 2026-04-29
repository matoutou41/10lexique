@echo off
REM ===================================================
REM  10lex - Build complet
REM  1. Genere dist\10lex.exe (PyInstaller)
REM  2. Genere installer_output\10lex-Setup-X.Y.Z.exe (Inno Setup)
REM ===================================================
setlocal

echo.
echo === Build 10lex ===
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo Telechargez Python 3.10+ : https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist "venv\" (
    echo [1/5] Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer venv.
        pause
        exit /b 1
    )
) else (
    echo [1/5] Environnement virtuel deja present.
)

echo [2/5] Activation de l'environnement...
call venv\Scripts\activate.bat

echo [3/5] Installation des dependances...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
pip install pyinstaller
if errorlevel 1 (
    echo [ERREUR] Installation des dependances echouee.
    pause
    exit /b 1
)

echo [4/5] Generation de l'icone...
python make_icon.py
if errorlevel 1 (
    echo [AVERTISSEMENT] Generation d'icone echouee, on continue.
)

echo [5/5] Generation de l'EXE...
if exist "build\" rmdir /S /Q build
if exist "dist\" rmdir /S /Q dist
if exist "10lex.spec" del /Q 10lex.spec

pyinstaller ^
    --onefile ^
    --windowed ^
    --name 10lex ^
    --icon assets\icon.ico ^
    --add-data "assets\icon.png;assets" ^
    --add-data "assets\icon.ico;assets" ^
    --hidden-import pystray._win32 ^
    --hidden-import PIL._tkinter_finder ^
    --hidden-import plyer.platforms.win.notification ^
    --collect-all anthropic ^
    --collect-all customtkinter ^
    --clean ^
    --noconfirm ^
    src\main.py

if errorlevel 1 (
    echo [ERREUR] Generation de l'EXE echouee.
    pause
    exit /b 1
)

if not exist "dist\10lex.exe" (
    echo [ERREUR] L'EXE n'a pas ete genere.
    pause
    exit /b 1
)

echo.
echo === EXE genere : dist\10lex.exe ===
echo.

REM ---- Inno Setup ----
echo Recherche d'Inno Setup...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    echo.
    echo === [INFO] Inno Setup n'est pas installe ===
    echo L'EXE autonome est pret : dist\10lex.exe
    echo Pour generer un INSTALLATEUR : telechargez Inno Setup 6 sur
    echo   https://jrsoftware.org/isdl.php
    echo Puis relancez ce build.bat
    echo.
    pause
    exit /b 0
)

echo Inno Setup trouve : %ISCC%
echo Generation de l'installateur...
"%ISCC%" installer.iss

if errorlevel 1 (
    echo [ERREUR] Generation de l'installateur echouee.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo  BUILD TERMINE !
echo ===================================================
echo  EXE autonome    : dist\10lex.exe
echo  Installateur    : installer_output\10lex-Setup-1.0.0.exe
echo ===================================================
echo.
pause
