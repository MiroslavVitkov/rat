#!/usr/bin/env python3


'''
Conferencing.
'''


from threading import Event, Thread

from impl import audio
from impl import conf
from impl import sock
from impl import video


def stream( death: Event=Event() ) -> None:
    '''Send captured chunks to a socket.'''

    def foo( s: sock.socket, death ):
        for chunk in audio.stream():
            s.sendall(chunk)

    sock.Server(foo, conf.AUDIO)


def watch( ip: str, death: Event=Event() ) -> None:
    '''Read from a socket and show with mpv.'''

    def foo( s: sock.socket ):
        watch( sock.recv(s) )

    sock.Client(lambda s: audio.watch(sock.recv(s)), ip, conf.AUDIO)


def test():
    death = Event()
    stream(death)
    watch('localhost', death)
    # Thread
    print('prot/media.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
