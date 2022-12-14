#!/usr/bin/env python3


'''
Communication sequences as to fufill top-level commands.
'''


import crypto
import name
import sock
from sock.socket import socket


def handshake_as_server( s: socket ) -> name.User:
    # After a client connects, send own pubkey unencrypted.
    send_pubkey(s)

    # Receive client's encrypted User object.
    client = recv_user(s)

    # Transmit own encrypted User object.
    send_user(s, client.pub)
    return client


def handshake_as_client( s: socket ) -> name.User:
    # After connecting, receive server unencrypted pubkey.
    server_pub = recv_pubkey(s)

    # Encrypt own User object with it and transmit it.
    send_user(s, server_pub)

    # Receive the server's encrypted User object.
    server = recv_user(s)
    return server


def send_pubkey( s: socket ) -> None:
    '''Transmit own public key unencrypted.'''
    _, pub = crypto.read_keypair()
    s.sendall(pub.save_pkcs1())


def recv_pubkey( s: socket ) -> crypto.Pub:
    key_data = sock.recv_one(s)
    pub = crypto.rsa.PublicKey.load_pkcs1(key_data)
    return pub


def send_user( s: socket
             , remote_pub: crypto.Pub ) -> None:
    own_priv, _ = crypto.read_keypair()
    sock.send(name.User().to_bytes(), s, own_priv, remote_pub)


def recv_user( s: socket ) -> name.User:
    data = sock.recv_one(s)
    remote_user = name.User.from_bytes(data)
    assert type(remote_user) == name.User, type(remote_user)
    return remote_user


def test():
    pass

if __name__ == '__main__':
    test()
