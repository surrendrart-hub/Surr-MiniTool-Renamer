@echo off
REM ============================================================
REM  Push initial du projet Surr - Renamer vers GitHub
REM  Repo : https://github.com/surrendrart-hub/Surr-MiniTool-Renamer
REM ============================================================

cd /d "%~dp0"
echo.
echo === Surr - Renamer : push vers GitHub ===
echo Dossier : %CD%
echo.

REM Verifier git
where git >NUL 2>&1
if errorlevel 1 (
    echo [ERREUR] Git n'est pas installe ou pas dans le PATH.
    echo Telecharger : https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Verifier si .git existe et est valide ; sinon (re)init
git -C "%CD%" rev-parse --git-dir >NUL 2>&1
if errorlevel 1 (
    if exist ".git" (
        echo [1/5] .git invalide detecte, nettoyage...
        rmdir /s /q ".git"
    )
    echo [1/5] git init...
    git init -b main
) else (
    echo [1/5] .git existant et valide
)

REM Identite (a personnaliser si besoin)
git config user.name  "surrendrart-hub"
git config user.email "surrendr.studio@gmail.com"

echo.
echo [2/5] Ajout des fichiers...
git add .

echo.
echo [3/5] Etat :
git status --short
echo.

REM Commit (skip si rien a committer)
git diff --cached --quiet
if errorlevel 1 (
    echo [4/5] Commit...
    git commit -m "Initial commit: Surr - Renamer v1.0 - powered by Surrendr.art"
) else (
    echo [4/5] Rien a committer
)

REM Remote
git remote get-url origin >NUL 2>&1
if errorlevel 1 (
    echo [5/5] Ajout du remote origin...
    git remote add origin https://github.com/surrendrart-hub/Surr-MiniTool-Renamer.git
) else (
    echo [5/5] Remote origin deja configure
)

echo.
echo === Push vers GitHub ===
echo (Une fenetre d'authentification peut s'ouvrir)
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo [ERREUR] Push echoue. Causes possibles :
    echo   - Repo distant non vide : faire d'abord 'git pull origin main --rebase'
    echo   - Authentification : configurer un Personal Access Token GitHub
    echo     https://