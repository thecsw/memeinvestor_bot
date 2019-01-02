#!/bin/bash

TEST_ENV=.testenv

if [ ! -d $TEST_ENV ]; then
  # set up virtual environment
  python3 -m venv $TEST_ENV
  source $TEST_ENV/bin/activate

  # install deps
  pip install -r requirements.txt
  pip install coverage
else
  # just activate virtual environment
  source $TEST_ENV/bin/activate
fi

# load envvars
set -a
source .env
set +a
export TEST=1
export BOT_ADMIN_REDDIT_ACCOUNTS=admin

# run tests
coverage run --branch --source=src -m unittest discover --start=test --pattern=*.py && \
  coverage report && \
  coverage html
