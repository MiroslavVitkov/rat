#!/usr/bin/env bash

nmap -p42666-42668 localhost | tail -n5 | head -n3
