#!/usr/bin/env python3


'''
Provide an interactive but machine parsable experience.
'''


import os
import socket
import sys


def get(name=os.getlogin(), group=None):
    if group is None:
        prompt = name + '-> '
    else:
        prompt = name + '@' + group + '-> '
    return prompt
