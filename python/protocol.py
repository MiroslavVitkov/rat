#!/usr/bin/env python3


'''
Communication sequences as to fufill top-level commands.
'''


import time

from socket import socket

import crypto
import name
import port
import sock


def handshake_as_server( s: socket ) -> name.User:
    # After a client connects, send own pubkey unencrypted.
    send_pubkey(s)

    # Receive client's encrypted User object.
    client = recv_user(s, None)

    # Transmit own encrypted User object.
    send_user(s, client.pub)
    return client


def handshake_as_client( s: socket ) -> name.User:
    # After connecting, receive server unencrypted pubkey.
    server_pub = recv_pubkey(s)

    # Encrypt own User object with it and transmit it.
    send_user(s, server_pub)

    # Receive the server's encrypted User object.
    server = recv_user(s, server_pub)
    return server


def send_msg( msg: str|bytes
            , s: socket
            , own_priv: crypto.Priv
            , remote_pub: crypto.Pub):
    if type(msg) == str:
        e = crypto.from_string(msg, own_priv, remote_pub)
    else:
        e = crypto.from_bin(msg, own_priv, remote_pub)
    s.sendall(e)


def recv_msg( s: socket
            , own_priv: crypto.Priv
            , remote_pub: crypto.Pub
            , alive: [bool]=[True]) -> bytes:
    '''
    Block until an entire message has been read out.
    A message is the longest sequence ending with a signature.
    On errors exceptions are reised.
    '''
    buf = b''
    for chunk in sock.recv(s, alive):
        try:
            d = crypto.from_bin(chunk, own_priv, remote_pub)
            buf += d
        except:
            crypto.verify(buf, chuk, remote_pub)
            return buf
    raise RuntimeError('Remote disconnected.')


### Details.
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
    key_data = s.recv(256)
    assert len(key_data) == 251, len(key_data)
    pub = parse_pubkey(key_data)
    return pub


def send_user( s: socket
             , remote_pub: crypto.Pub ) -> None:
    own_priv, _ = crypto.read_keypair()
    u = name.User().to_bytes()  # 282 bytes
    send_msg(u, s, own_priv, remote_pub)


def recv_user( s: socket, remote_pub: crypto.Pub ) -> name.User:
    '''Receive remote User object encrypted and signed.
       A copy-ast of recv_msg() which however allows None.
    '''
    own_priv, _ = crypto.read_keypair()

    decr = b''
    for chunk in sock.recv(s):
        try:
            d = crypto.decrypt(chunk, own_priv)
            decr += d
        except:
            user = name.User.from_bytes(decr)
            if remote_pub is None:
                remote_pub = user.pub
            crypto.verify(decr, chunk, remote_pub)
            return user


def test_crypto_sane():
    assert crypto.read_keypair()[1] == parse_pubkey( emit_pubkey() )

    priv, pub = crypto.read_keypair()
    e = crypto.from_string('something', priv, pub)
    assert crypto.to_string(e, priv, pub) == 'something'


class SocketMock:
    def __init__(me):
        me.buf = b''

    def send(me, msg):
        me.buf += msg

    def recv(me, max=1024):
        assert len(me.buf) < max
        tmp = me.buf
        me.buf = b''
        return tmp

    def settimeout(me, val):
        pass

    def sendall(me, msg):
        me.send(msg)


def test_sockmock():
    s = SocketMock()
    s.send(b'Mock sockets as we are trying to deal only with protocol here.')
    print(s.recv())
    assert len(s.buf) == 0


def test_send_recv_msg():
    msg = str(list(range(101)))
    priv, pub = crypto.read_keypair()  # Send to ourselves.

    def silent_recv(s, a):
        buf = b''
        for chunk in sock.recv(s):
            try:
                d = crypto.decrypt(chunk, priv)
                buf = buf + d
            except:
                crypto.verify(buf, chunk, pub)
                print('Decrypted and verified incoming message:', buf.decode('utf8'))

    def client_send(s):
        s.sendall(crypto.from_string(msg, priv, pub))

    server = sock.Server(silent_recv)
    client = sock.Client(client_send)

    server.alive[0] = False


def test_send_recv_pubkey() -> None:
    _, pub = crypto.read_keypair()
    received = []
    server = sock.Server(lambda s, _: send_pubkey(s))
    sock.Client(lambda s: received.append(recv_pubkey(s)))
    assert received[0] == pub, received[0]
    server.alive[0] = False


def test_send_recv_user() -> None:
    '''Exchange user objects having reliably exchanged public keys.'''
    _, pub = crypto.read_keypair()
    received = []
    server = sock.Server(lambda s, _: received.append(recv_user(s, pub)))
    sock.Client(lambda s: send_user(s, pub))
    time.sleep(1)
    assert received[0] == name.User(), received[0]
    server.alive[0] = False


def test_handshake():
    server = sock.Server(lambda s, _: handshake_as_server(s))
    client = sock.Client(handshake_as_client)
    server.alive[0] = False


def test():
    test_crypto_sane()
    test_sockmock()
    test_send_recv_msg()
    test_send_recv_pubkey()
    test_send_recv_user()
    test_handshake()

    print('protocol.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
