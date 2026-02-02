@echo off
REM Setup git hooks for the MongoDB Labs repository (Windows)

echo Setting up git hooks...

REM Set git hooks path to .githooks directory
git config core.hooksPath .githooks

echo.
echo Git hooks configured!
echo.
echo The following hooks are now active:
echo   - pre-commit: Checks if lab index is up-to-date
echo.
echo To disable hooks, run:
echo   git config --unset core.hooksPath