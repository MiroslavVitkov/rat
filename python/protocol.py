#!/usr/bin/env python3


'''
Communication sequences as to fufill top-level commands.
'''


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
        e = crypto.from_str(msg, own_priv, remote_pub)
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
    for data in recv(s, alive):
        try:
            d = crypto.from_bin(data, own_priv, remote_pub)
            buf = buf + d
        except:
            verify(buf, data, remote_pub)
            return buf
    raise runtime_error('Remote disconnected.')


### Details.
def emit_pubkey() -> bytes:
    '''Convert rsa.PublicKey to a format suitable to be transmitted.'''
    _, pub = crypto.read_keypair()
    return pub.save_pkcs1()


def send_pubkey( s: socket ) -> None:
    '''Transmit own public key unencrypted.'''
    s.sendall( emit_pubkey() )  # 251 bytes


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
       Basically a re-implementation of recv_msg() which allows None.
    '''
    own_priv, _ = crypto.read_keypair()
    data = s.recv(4096)  # We get four 128 byte packets.
    packets = crypto.chop(data, crypto.CHUNK_BYTES)
    decr = crypto.stitch([crypto.decrypt(p, own_priv) for p in packets[:-1]])
    user = name.User.from_bytes(decr)
    if remote_pub is None:
        remote_pub = user.pub
    crypto.verify(decr, packets[-1], remote_pub)
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


def test_handshake():
    server = sock.Server(port.TEST, lambda s, _: print( s.recv(64) ))
    client = sock.Client('localhost'
                        , port.TEST
                        , lambda s: s.sendall('Protocol Test One'.encode('utf8')))
    server.alive[0] = False


def test():
    test_crypto_sane()
    test_sockmock()
    test_handshake()

    print('protocol.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
