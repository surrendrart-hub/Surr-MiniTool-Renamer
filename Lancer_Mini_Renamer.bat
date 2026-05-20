@echo off
REM Lance Mini Renamer (Windows). Double-cliquer pour ouvrir.
cd /d "%~dp0"

REM Installe tkinterdnd2 si absent (drag & drop)
python -c "import tkinterdnd2" 2>NUL
if errorlevel 1 (
    echo Installation de tkinterdnd2 ^(drag ^& drop^)...
    python -m pip install --quiet tkinterdnd2
)

python "%~dp0mini_renamer.py"
if errorlevel 1 pause
