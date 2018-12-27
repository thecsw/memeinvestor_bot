#!/bin/bash

# set up virtual environment
python3 -m venv .testenv
source .testenv/bin/activate

# install deps
pip install -r requirements.txt

# load envvars
set -a
source .env
set +a

# run tests
python test/main.py
