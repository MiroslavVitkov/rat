#!/usr/bin/env bash

# In this file: scan rat's ports status.

nmap -p42666-42668 localhost | tail -n5 | head -n3
