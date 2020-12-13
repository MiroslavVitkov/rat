#!/usr/bin/env python3


'''
A peer to peer chat client.
Refer to the README for dessign goals and usage.
'''


import crypto
import pack
import sock
import time


PORT = 42666


def send(text: str
        , s: sock.socket.socket
        , own_priv: crypto.Priv
        , recepient_pub: crypto.Pub):
    signature = crypto.sign(text, own_priv)
    encrypted = crypto.encrypt(text, recepient_pub)
    msg = pack.Packet(encrypted, signature).to_bytes()
    s.sendall(msg)


def listen(s: sock.socket.socket):
    for i in range (10):
        data = s.recv(1024)
        if data:
            print('RECEIVED:', data)
            i += 10
        time.sleep(0.1)


def receive_one( s: sock.socket.socket
               , own_priv: crypto.Priv
               , sender_pub: crypto.Pub):
    '''Blocks until one message has been read and decoded.'''
    while True:
        data = s.recv(1024)
        if data:
            packet = pack.Packet.from_bytes(data)
            text = crypto.decrypt(packet.encrypted, own_priv)
            crypto.verify(text, packet.signature, sender_pub)
            return text
        time.sleep(0.1)


class Rat:
    '''A rodent.'''
    def __init__(me):
        me.priv, me.pub = crypto.generate_keypair()
        def listen2(s):
            t = receive_one(s, me.priv, me.pub)
            print(t)
        me.server = sock.Server(PORT, listen2)


    def connect(me, ip: str):
        def func(s: sock.socket.socket):
            send('Hello World!', s, me.priv, me.pub)

        import time
        time.sleep(2)
        client = sock.Client(ip, PORT, func)
        time.sleep(2)
        me.server.alive = False


def test():
    sock.test()
    crypto.test()
    pack.test()
    print('ALL UNIT TESTS PASSED')
    print()

    time.sleep(5)
    r = Rat()
    r.connect('192.168.0.100')
    print('INTEGRATION TEST PASSED')
    print()


if __name__ == '__main__':
    import sys

    # rat test - run all tests of the program
    if sys.argv[1] == 'test':
        test()

    # rat listen - accept connections on port PORT
    if sys.argv[1] == 'listen':
        r = Rat()

    # rat connect 24.69.09.11
    if sys.argv[1] == 'connect':
        ip = sys.argv[2]
        r = Rat()
        r.connect(ip)
