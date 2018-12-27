#!/bin/bash

TEST_ENV=.testenv

if [ ! -d $TEST_ENV ]; then
  # set up virtual environment
  python3 -m venv $TEST_ENV
  source $TEST_ENV/bin/activate

  # install deps
  pip install -r requirements.txt
else
  # just activate virtual environment
  source $TEST_ENV/bin/activate
fi

# load envvars
set -a
source .env
set +a

# run tests
TEST=1 python test/main.py
