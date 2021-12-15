#!/usr/bin/env python3


'''
Config file perser.
'''


from configparser import ConfigParser


def get(path: str='../conf.ini', c: list=[]):
    '''
    Use like:
        get_conf()['section_name']['setting_name']
    '''
    if not len(c):
        c_ = ConfigParser()
        c_.read(path)
        c.append(c_)

    return c[0]


def test():
    assert(get()['user']['name'])
    assert(get()['user']['group'])
    assert(get()['user']['status'])
    assert(get()['user']['keypath'])
    print('conf.py: ALL TESTS PASSED')


if __name__ == '__main__':
    test()
