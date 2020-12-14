#!/usr/bin/env python3


'''
Provide an interactive but machine parsable experience.
'''


import os
import socket
import sys


def get():
    name = os.getlogin()
    host = socket.gethostname()
    prompt = name + '@' + host + ' '
    return prompt
