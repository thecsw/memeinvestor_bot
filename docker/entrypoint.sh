#!/bin/sh
envsubst < /config.py > config.py

exec "$@"
