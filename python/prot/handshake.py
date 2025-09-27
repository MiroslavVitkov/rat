#!/usr/bin/env python3


'''
Exchange public keys.
'''


import time

from socket import socket

from impl import conf
from impl import crypto
from impl import sock

from prot.chat import send_msg
from prot.name import User


def as_server( s: socket ) -> User:
    # This is to prevent port scanners from fingerprinting rat.
    if not recv_pepper(s):
        print('Wrong pepper', s)
        return

    # After a client connects, send own pubkey unencrypted.
    send_pubkey(s)

    # Receive client's encrypted User object.
    client = recv_user(s, None)

    # Transmit own encrypted User object.
    send_user(s, client.pub)
    return client


def as_client( s: socket ) -> User:
    send_pepper(s)

    # After connecting, receive server unencrypted pubkey.
    server_pub = recv_pubkey(s)

    # Encrypt own User object with it and transmit it.
    send_user(s, server_pub)

    # Receive the server's encrypted User object.
    server = recv_user(s, server_pub)
    return server


### Details.
def send_pepper( s: socket ) -> None:
    pepper = conf.get()['crypto']['pepper']
    s.sendall( pepper.encode('utf8') )


def recv_pepper( s: socket ) -> bool:
    if s.recv(1024).decode('utf8') == conf.get()['crypto']['pepper']:
        return True
    else:
        return False


def emit_pubkey() -> bytes:
    '''Convert rsa.PublicKey to a format suitable to be transmitted.'''
    _, pub = crypto.read_keypair()
    return pub.save_pkcs1()


def send_pubkey( s: socket ) -> None:
    '''Transmit own public key unencrypted.'''
    key = emit_pubkey()  # 251 bytes
    s.sendall( key )


def parse_pubkey( b: bytes) -> crypto.Pub:
    '''Parses whatever emit_pubkey() generated back to a class instance.'''
    return crypto.rsa.PublicKey.load_pkcs1(b)


def recv_pubkey( s: socket ) -> crypto.Pub:
    '''Receive unencrypted remote public key.'''
    key_data = s.recv(1024)
    pub = parse_pubkey(key_data)
    return pub


def send_user( s: socket
             , remote_pub: crypto.Pub ) -> None:
    own_priv, _ = crypto.read_keypair()
    u = User().to_bytes()  # 282 bytes
    send_msg(u, s, own_priv, remote_pub)


def recv_user( s: socket, remote_pub: crypto.Pub ) -> User:
    '''Receive remote User object encrypted and signed.
       A copy-ast of chat.recv_msg() which however allows None.
    '''
    own_priv, _ = crypto.read_keypair()

    decr = b''
    for chunk in sock.recv(s):
        try:
            d = crypto.decrypt(chunk, own_priv)
            decr += d
        except:
            user = User.from_bytes(decr)
            if remote_pub is None:
                remote_pub = user.pub
            crypto.verify(decr, chunk, remote_pub)
            return user


def test_send_recv_pubkey() -> None:
    _, pub = crypto.read_keypair()
    received = []
    server = sock.Server(lambda s, _: send_pubkey(s))
    sock.Client(lambda s: received.append(recv_pubkey(s)))

    assert received[0] == pub, received[0]
    server.alive.set()
    time.sleep(sock.POLL_PERIOD)


def test_send_recv_user() -> None:
    '''Exchange user objects having reliably exchanged public keys.'''
    _, pub = crypto.read_keypair()
    received = []
    server = sock.Server(lambda s, _: received.append(recv_user(s, pub)))
    sock.Client(lambda s: send_user(s, pub))

    time.sleep(1)
    assert received[0] == User(), received[0]
    server.alive.set()
    time.sleep(sock.POLL_PERIOD)


def test_handshake():
    server = []
    client = []
    s = sock.Server(lambda s, _: client.append(as_server(s)))
    sock.Client(lambda s: server.append(as_client(s)))

    time.sleep(1)
    assert server[0] == client[0] == User()
    s.alive.set()
    time.sleep(sock.POLL_PERIOD)


def test():
    test_send_recv_pubkey()
    test_send_recv_user()
    test_handshake()

    print('prot/handhske.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
