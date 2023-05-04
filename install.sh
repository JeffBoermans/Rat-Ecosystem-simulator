#!/usr/bin/env bash

# Setup venv
echo "[Install] Setup python virtual env";
python3 -m venv venv;
. venv/bin/activate;

# Install reqs
echo "[Install] Install dependencies";
pip install -r requirements.txt;
