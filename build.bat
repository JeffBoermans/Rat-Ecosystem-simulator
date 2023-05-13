SET DIR=build

REM Setup build output location
echo "[Build] Setup build dir"
venv/Scripts/activate
if not exist %DIR% mkdir %DIR%

REM Build the project into an executable
echo "[Build] Build executable at %DIR%"
cd %DIR%
pyinstaller -F "%CD%\..\main.py"
echo "[Build] Done"