#!/usr/bin/env python3


'''
Send and receive text messages over an esteblished channel.
'''


import time

from socket import socket
from threading import Event

from impl import crypto
from impl import sock


def send_msg( msg: str|bytes
            , s: socket
            , own_priv: crypto.Priv
            , remote_pub: crypto.Pub):
    if type(msg) == str:
        e = crypto.from_string(msg, own_priv, remote_pub)
    else:
        e = crypto.from_bin(msg, own_priv, remote_pub)
    s.sendall(e)


def recv_msg( s: socket
            , own_priv: crypto.Priv
            , remote_pub: crypto.Pub
            , death: Event=Event()) -> bytes:
    '''
    Block until an entire message has been read out.
    A message is the longest sequence ending with a signature.
    '''
    buf = b''
    for chunk in sock.recv(s, death):
        try:
            d = crypto.decrypt(chunk, own_priv)
            buf += d
        except:
            crypto.verify(buf, chunk, remote_pub)
            return buf
    raise RuntimeError('Remote disconnected.')


def test_send_recv_msg():
    msg = str(list(range(101)))
    priv, pub = crypto.read_keypair()  # Send to ourselves.

    def silent_recv(s, a):
        buf = b''
        for chunk in sock.recv(s):
            try:
                d = crypto.decrypt(chunk, priv)
                buf = buf + d
            except:
                crypto.verify(buf, chunk, pub)
                print('Decrypted and verified incoming message:', buf.decode('utf8'))

    def client_send(s):
        s.sendall(crypto.from_string(msg, priv, pub))

    server = sock.Server(silent_recv)
    client = sock.Client(client_send)

    server.death.set()
    time.sleep(sock.POLL_PERIOD)


def test():
    test_send_recv_msg()

    print('prot/chat.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
