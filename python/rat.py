#!/usr/bin/env python3


'''
A peer to peer chat client.
Refer to the README for dessign goals and usage.
'''


import crypto
import pack
import sock


# TODO
priv, pub = crypto.generate_keypair()


def send(text: str
        , s: sock.socket.socket
        , own_priv: crypto.Priv
        , recepient_pub: crypto.Pub):
    signature = crypto.sign(text, priv)
    encrypted = crypto.encrypt(text, recepient_pub)
    msg = Packet(encrypted, signature)
    s.sendall(msg.encrypted + msg.signature)


def receive_one(s: sock.socket.socket
                , own_priv: crypto.Priv
                , sender_pub: crypto.Pub):
    '''Blocks until one message has been read and decoded.'''
    while True:
        time.sleep(0.1)
        data = s.recv(1024)
        if data:
            import traceback
            traceback.print_stack()
            print('NOW LETS READ')

            packet = Packet.from_bytes(data)
            text = crypto.decrypt(packet.encrypted, priv)
            #crypto.verify(text, packet.signature, pub)
            return text


def test():
    sock.test()
    crypto.test()
    pack.test()
    print('ALL TESTS PASSED')


if __name__ == '__main__':
    test()
