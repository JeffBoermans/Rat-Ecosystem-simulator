@echo off

REM Setup venv
echo "[Install] Setup python virtual env"
python3 "-m" "venv" "venv"
. "venv\bin\activate"

REM Install reqs
echo "[Install] Install dependencies"
pip "install" "-r" "requirements.txt"