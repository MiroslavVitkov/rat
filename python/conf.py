#!/usr/bin/env python3


'''
Configuration povider, mainly via a config file parser, but ports are hardcoded.
'''


from configparser import ConfigParser
import os


# Standard ports used by the program.
CHATSERVER = 42666
NAMESERVER = CHATSERVER + 1
VIDEO = NAMESERVER + 1
TEST = VIDEO + 1
RELAY_0 = TEST+1


def where_are_we():
    '''
    Return path to the dir containing this file.
    Otherwise relative paths are relative to the working dir
    and that is the dir the script was invoked from.
    '''
    file_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(file_path)
    return dir_path


def get(path: str=where_are_we()+'/../conf.ini', c: list=[]):
    '''
    Use like:
        get()['section_name']['setting_name']
    '''
    if not len(c):
        c_ = ConfigParser()
        c_.read(path)
        c.append(c_)

    return c[0]


def get_keypath():
    p = get()['crypto']['keypath']
    return os.path.expanduser(p)


def test():
    # Ensure fields exist and are non-empty.
    assert len(get()['about']['name'])
    assert len(get()['about']['group'])
    assert len(get()['about']['status'])
    assert len(get()['crypto']['keypath'])
    # ['user']['bots'] is empty by default.

    print('conf.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
