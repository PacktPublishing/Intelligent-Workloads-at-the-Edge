#!/bin/bash

python3 -m venv env
env/bin/python -m pip install -r requirements.txt
FILE=rootca.pem
if [ -f "$FILE" ]; then
    echo "$FILE exists, skipping provision-thing.py. Delete pem files in this directory to reprovision."
else 
    echo "$FILE does not exist, running provision-thing.py"
    env/bin/python provision-thing.py
fi

echo "Starting discovery.py, quit with Ctrl+C"
env/bin/python discover.py