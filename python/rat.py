#!/usr/bin/env python3


'''
A peer to peer chat client.
Refer to the README for dessign goals and usage.
'''


import crypto
import pack
import sock


def send(text: str
        , s: sock.socket.socket
        , own_priv: crypto.Priv
        , recepient_pub: crypto.Pub):
    signature = crypto.sign(text, own_priv)
    encrypted = crypto.encrypt(text, recepient_pub)
    msg = pack.Packet(encrypted, signature)
    s.sendall(msg.encrypted + msg.signature)


def listen(s: sock.socket.socket):
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
        port = 42666

        me.server = sock.Server(port, listen)

        import time
        time.sleep(1)

        def say_hello(s):
            send('Hello World!', s, me.priv, me.pub)
        me.client = sock.Client('localhost', port, say_hello)
        time.sleep(1)

        me.server.alive = False


def receive_one(s: sock.socket.socket
                , own_priv: crypto.Priv
                , sender_pub: crypto.Pub):
    '''Blocks until one message has been read and decoded.'''
    while True:
        time.sleep(0.1)
        data = s.recv(1024)
        if data:
            packet = Packet.from_bytes(data)
            text = crypto.decrypt(packet.encrypted, priv)
            crypto.verify(text, packet.signature, pub)
            return text


def test():
    sock.test()
    crypto.test()
    pack.test()
    print('ALL UNIT TESTS PASSED')
    print()

    sock.time.sleep(10)
    r = Rat()
    print('INTEGRATION TEST PASSED')
    print()


if __name__ == '__main__':
    test()
