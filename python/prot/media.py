#!/usr/bin/env python3


'''
Conferencing.
'''


from threading import Event

from impl import audio
from impl import conf
from impl import sock
from impl import video


def stream( death: Event=Event() ) -> None:
    def foo( s: sock.socket, _ ):
        for chunk in audio.stream():
            s.sendall(chunk)

    sock.Server(foo, conf.AUDIO)


def watch():
    def foo( s:sock.socket ):
        for chunk in sock.recv(s):
            print(len(chunk))

    sock.Client(foo, 'localhost', conf.AUDIO)


def test():
    print('prot/media.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
