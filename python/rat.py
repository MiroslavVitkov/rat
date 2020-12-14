#!/usr/bin/env python3


'''
A peer to peer chat client.
Refer to the README for dessign goals and usage.
'''


import time

import bot
import crypto
import pack
import sock


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
               , remote_pub: crypto.Pub):
    '''Blocks until one message has been read and decoded.'''
    while True:
        data = s.recv(1024)
        if data:
            packet = pack.Packet.from_bytes(data)
            text = crypto.decrypt(packet.encrypted, own_priv)
            crypto.verify(text, packet.signature, remote_pub)
            return text
        time.sleep(0.1)


def listen():
        own_priv, own_pub = crypto.read_keypair(SECRET)
        remote_pub = None

        def forever(s):
            while True:
                data = s.recv(1024)
                if data:
                    remote_pub = crypto.Pub.load_pkcs1(data)
                    s.sendall(own_pub.save_pkcs1())
                    break

            while True:
                t = receive_one(s, own_priv, remote_pub)
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
    own_priv, own_pub = crypto.generate_keypair()
    remote_pub = None

    def func(s: sock.socket.socket):
        s.sendall(own_pub.save_pkcs1())
        # Receive server public key.
        while True:
            data = s.recv(1024)
            if data:
                remote_pub = crypto.Pub.load_pkcs1(data)
                break

        while True:
             insult = bot.curse()
             send(insult, s, own_priv, remote_pub)
             time.sleep(bot.random.randint(1,8))

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
