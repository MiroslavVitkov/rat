#!/usr/bin/env bash

# In this file: status bar for files in a python repo.

git status | grep 'On branch'
git status | grep .py
