@echo off
REM Launch the Nonparametric Statistics Agent.
REM Double-click this file, or run run.bat in a terminal.
chcp 65001 >nul
pushd "%~dp0"
set PYTHONUTF8=1
".venv\Scripts\python.exe" -m src.cli
echo.
pause >nul
popd
