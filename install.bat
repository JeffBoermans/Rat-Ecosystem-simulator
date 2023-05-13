@echo off

REM Setup venv
echo "[Install] Setup python virtual env"
python -m venv venv
rem .\venv\Scripts\activate

REM Install reqs
echo "[Install] Install dependencies"
pip install -r requirements.txt