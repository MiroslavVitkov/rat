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
SECRET = '/tmp/whatever483055'

def test():
    sock.test()
    crypto.test()
    pack.test()
    print('UNIT TESTS PASSED')
    print()

    time.sleep(5)
#    r = Rat()
#    r.connect('192.168.0.100')
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
        priv, pub = crypto.read_keypair(SECRET)
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
    priv, pub = crypto.read_keypair(SECRET)
    def func(s: sock.socket.socket):
        while True:
             send('Hello World!', s, priv, pub)
             time.sleep(1)
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
    elif sys.argv[1] == 'test':
        test()
    elif sys.argv[1] == 'listen':
        listen()
    elif sys.argv[1] == 'connect':
        connect(sys.argv[2])
    else:
        print(sys.argv[1], '- command not recognised')
        print_help()
