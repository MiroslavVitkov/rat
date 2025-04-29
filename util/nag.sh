#!/usr/bin/env bash


# In this file: nag to someone. Possibly very quickly and from numerous remotes.


IP=46.10.210.37
INTERVAL=0  # seconds

while true; do
~/proj/rat/python/rat.py say "$IP" myrzi me
~/proj/rat/python/rat.py say "$IP" Всички в ХД са гейове.
sleep "$INTERVAL"
done
