@echo off

SET DIR=build\

REM Setup build output location
echo "[Build] Setup build dir"
. "venv\bin\activate"
if not exists (
    mkdir %DIR%
)

REM Build the project into an executable
echo "[Build] Build executable at %DIR%"
cd %DIR%
pyinstaller -F "%CD%\..\main.py"
echo "[Build] Done"