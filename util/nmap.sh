#!/usr/bin/env bash

# In this file: scan rat's ports status.
#               Intended as a mini status bar with sleep().

nmap -p42666-42670 pi | tail -n7 | head -n5
