#!/usr/bin/env python3


'''
Provide an interactive but machine parsable experience.
'''


import conf


def get( name: str=conf.get()['user']['name']
       , group:str=conf.get()['user']['group']
       ) -> str:
    return (name + '@' + group + '<-')


def test():
    print('Default prompt is', get())
    print('prompt.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
