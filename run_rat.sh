#!/usr/bin/env sh

# Keep rat alive forever.
# Intended to be invoked every minute via cron.

rat=~/proj/rat/python/rat.py

results=$(ps -aux | grep rat.py)

echo "$results" | grep relay > /dev/null
if [ "$?" -eq 1 ]; then
    "$rat" relay &
fi

echo "$results" | grep serve > /dev/null
if [ "$?" -eq 1 ]; then
    "$rat" serve &
fi
