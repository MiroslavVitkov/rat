#!/usr/bin/env python3


'''
Communication sequences as to fufill top-level commands.
'''


from socket import socket

import crypto
import name
import sock


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


def emit_pubkey() -> bytes:
    '''Convert rsa.PublicKey to a format suitable to be transmitted.'''
    _, pub = crypto.read_keypair()
    return pub.save_pkcs1()


def send_pubkey( s: socket ) -> None:
    '''Transmit own public key unencrypted.'''
    s.sendall( emit_pubkey() )


def parse_pubkey( b: bytes) -> crypto.Pub:
    '''Parses whatever emit_pubkey() generated back to a class instance.'''
    return crypto.rsa.PublicKey.load_pkcs1(b)


def recv_pubkey( s: socket ) -> crypto.Pub:
    '''Receive unencrypted remote public key.'''
    key_data = sock.recv_one(s)
    pub = parse_pubkey(key_data)
    return pub


def send_user( s: socket
             , remote_pub: crypto.Pub ) -> None:
    own_priv, _ = crypto.read_keypair()
    u = name.User().to_bytes()
    sock.send(u, s, remote_pub, own_priv)


def recv_user( s: socket ) -> name.User:
    '''Receive remote User object encrypted by our pubkey.'''
    encrypted = sock.recv_one(s)
    own_priv, _ = crypto.read_keypair()
    data = crypto.decrypt(encrypted, own_priv)
    assert data  # on error decrypt() returns ''
    remote_user = name.User.from_bytes(bytes(data, 'utf8'))
    assert type(remote_user) == name.User, type(remote_user)
    return remote_user


def test():
    assert crypto.read_keypair()[1] == parse_pubkey( emit_pubkey() )
    print('UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
