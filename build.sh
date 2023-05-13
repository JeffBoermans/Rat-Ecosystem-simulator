# #!/usr/bin/env bash

DIR="build"

# Setup build output location
echo "[Build] Setup build dir";
. venv/bin/activate;
[ ! -d "$DIR" ] && mkdir $DIR

# Build the project into an executable
echo "[Build] Build executable at $DIR";
cd $DIR
pyinstaller -F ../main.py
echo "[Build] Done";
