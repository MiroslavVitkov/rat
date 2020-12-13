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



def listen_orig(s: sock.socket.socket):
    for i in range (10):
        data = s.recv(1024)
        if data:
            print('RECEIVED:', data)
            i += 10
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


def listen():
        priv, pub = crypto.generate_keypair()
        def forever(s):
            while True:
                t = receive_one(s, priv, pub)
                print(t)
        server = sock.Server(PORT, forever)


def send( text: str
        , s: sock.socket.socket
        , own_priv: crypto.Priv
        , recepient_pub: crypto.Pub):
    signature = crypto.sign(text, own_priv)
    encrypted = crypto.encrypt(text, recepient_pub)
    msg = pack.Packet(encrypted, signature).to_bytes()
    s.sendall(msg)


def connect(ip: str):
    priv, pub = crypto.generate_keypair()
    def func(s: sock.socket.socket):
         send('Hello World!', s, priv, pub)
    client = sock.Client(ip, PORT, func)


def print_help():
    print('Usage:')
    print('rat test - run all tests of the program')
    print('rat listen - accept connections on port', PORT)
    print('rat connect xx.xx.xx.xx - start chatting if they are listening')


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2 or sys.argv[1] == 'help':
        print_help()
        sys.exit()

    if sys.argv[1] == 'test':
        test()
        sys.exit()

    if sys.argv[1] == 'listen':
        r = Rat()
        sys.exit()

    if sys.argv[1] == 'connect':
        ip = sys.argv[2]
        r = Rat()
        r.connect(ip)
        sys.exit()
