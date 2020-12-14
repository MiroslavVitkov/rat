#!/usr/bin/env python3


'''
A peer to peer chat client.
Refer to the README for dessign goals and usage.
'''


from threading import Thread
import time

import bot
import crypto
import pack
import prompt
import sock


PORT = 42666


def get_extern_ip():
    import requests
    f = requests.request('GET', 'http://myip.dnsomatic.com')
    ip = f.text


def handshake(s: sock.socket.socket, own_pub: crypto.Pub) -> crypto.Pub:
    '''Exchange public keys in cleartext!'''
    while True:
        data = s.recv(1024)
        if data:
            remote_pub = crypto.Pub.load_pkcs1(data)
            s.sendall(own_pub.save_pkcs1())
            return remote_pub


def send( text: str
        , s: sock.socket.socket
        , own_priv: crypto.Priv
        , remote_pub: crypto.Pub
        ) -> None:
    signature = crypto.sign(text, own_priv)
    encrypted = crypto.encrypt(text, remote_pub)
    msg = pack.Packet(encrypted, signature).to_bytes()
    s.sendall(msg)


def handle_input( s: sock.socket.socket
                , own_priv: crypto.Priv
                , remote_pub: crypto.Pub
                ) -> None:
    '''
    We need 2 threads to do simultaneous input and output.
    So let's use the current thread for listening and span an input one.
    '''
    def inp():
        while True:
            text = input(prompt.get())
            send(text, s, own_priv, remote_pub)
    Thread(target=inp).start()


def listen():
        own_priv, own_pub = crypto.generate_keypair()
        remote_pub = None

        def forever(s):
            # Handshake.
            while True:
                data = s.recv(1024)
                if data:
                    remote_pub = crypto.Pub.load_pkcs1(data)
                    s.sendall(own_pub.save_pkcs1())
                    break

            handle_input(s, own_priv, remote_pub)

            # Accept text messages.
            while True:
                data = s.recv(1024)
                if data:
                    packet = pack.Packet.from_bytes(data)
                    text = crypto.decrypt(packet.encrypted, own_priv)
                    crypto.verify(text, packet.signature, remote_pub)
                    print(text)
                time.sleep(0.1)

        server = sock.Server(PORT, forever)


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

        handle_input(s, own_priv, remote_pub)

        # Accept text messages.
        while True:
            data = s.recv(1024)
            if data:
                packet = pack.Packet.from_bytes(data)
                text = crypto.decrypt(packet.encrypted, own_priv)
                crypto.verify(text, packet.signature, remote_pub)
                print(text)
            time.sleep(0.1)

        while False:
             insult = bot.curse()
             send(insult, s, own_priv, remote_pub)
             time.sleep(bot.random.randint(1,8))

    client = sock.Client(ip, PORT, func)


def test():
    sock.test()
    crypto.test()
    pack.test()
    time.sleep(2)
    print('UNIT TESTS PASSED')
    print()

    Thread(target=listen).start()
    time.sleep(1)
    Thread(target=connect, args=['localhost']).start()
    print('INTEGRATION TEST PASSED')
    print()


def print_help():
    print('Usage:')
    print('rat listen - accept connections on port', PORT)
    print('rat connect xx.xx.xx.xx - start chatting if they are listening')
    print('rat test - run all tests of the program')


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2 or sys.argv[1] == 'help':
        print_help()
    elif sys.argv[1] == 'listen':
        listen()
    elif sys.argv[1] == 'connect':
        connect(sys.argv[2])
    elif sys.argv[1] == 'test':
        test()
    else:
        print(sys.argv[1], '- command not recognised')
        print_help()
