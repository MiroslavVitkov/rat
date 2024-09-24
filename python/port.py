#!/usr/bin/env python3


'''
Standard ports used by the program.
'''


CHATSERVER = 42666
NAMESERVER = CHATSERVER + 1
TEST = NAMESERVER + 1


def test():
    print('port.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    print('rat listens for peers on', CHATSERVER,
          'and provides names on', NAMESERVER)
    test()
