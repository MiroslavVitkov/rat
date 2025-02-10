#!/usr/bin/env python3


'''
Communication sequences as to fufill top-level commands.
'''


import time

from socket import socket

import conf
import crypto
import sock


def handshake_as_server( s: socket ) -> conf.User:
    # After a client connects, send own pubkey unencrypted.
    send_pubkey(s)

    # Receive client's encrypted User object.
    client = recv_user(s, None)

    # Transmit own encrypted User object.
    send_user(s, client.pub)
    return client


def handshake_as_client( s: socket ) -> conf.User:
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
            d = crypto.decrypt(chunk, own_priv)
            buf += d
        except:
            crypto.verify(buf, chunk, remote_pub)
            return buf
    raise RuntimeError('Remote disconnected.')


class NameServer:
    '''
    A server where users publish their (nickname, public key, ip, comment)
    for everyone to see.

    Groups look like regular users and are regular users,
    they just retransmit anything they receive to everyone else.
    '''
    def __init__(me):
        me.users = {}
        me.alive = [True]

        me.server = sock.Server(me._handle, conf.NAMESERVER)
        me.server.alive = me.alive
        me.priv, _ = crypto.read_keypair()


    def register(me, u: conf.User) -> None:
        assert type(u) == conf.User, type(u)
        me.users[u.pub] = u


    def _handle(me, s: socket, alive: [bool]) -> None:
        client = protocol.handshake_as_server(s)
        for msg in protocol.recv_msg(s, priv, client.pub):
            print(len(msg))

    def _handle2(me, s: socket) -> None:
        for data in sock.recv(s, me.alive):
            # Accept remote User object.
            remote_user = conf.User.from_bytes(data)
            assert type(remote_user) == conf.User, type(remote_user)

            # This could be an `ask` or a `register` request.
            text = data.decode('utf-8')
            if text == 'register':
                me.register(remote_user)
                print('New user registered:', remote_user)
                print('Now there are', len(me.users), 'registered users.\n')
            else:
                print(s.getsockname(), 'is asking for', text)
                try:
                    r = re.compile(text)
                except:
#                    sock.send( b'Invalid regular expression!'
#                             , s, own_priv, remote_pub )
                    continue

                matches = [me.users[u] for u in me.users
                           if r.match(me.users[u].name)]
                if not matches:
#                    sock.send( b'No matches!'
#                             , s, own_priv, remote_user.pub )
                    continue

#                for u in matches:
#                    bytes = pickle.dumps(u)
#                    sock.send(bytes, s, own_priv, remote_user.pub)


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
    u = conf.User().to_bytes()  # 282 bytes
    send_msg(u, s, own_priv, remote_pub)


def recv_user( s: socket, remote_pub: crypto.Pub ) -> conf.User:
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
            user = conf.User.from_bytes(decr)
            if remote_pub is None:
                remote_pub = user.pub
            crypto.verify(decr, chunk, remote_pub)
            return user


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
    assert received[0] == conf.User(), received[0]
    server.alive[0] = False


def test_handshake():
    server = []
    client = []
    s = sock.Server(lambda s, _: client.append(handshake_as_server(s)))
    sock.Client(lambda s: server.append(handshake_as_client(s)))

    time.sleep(1)
    assert server[0] == client[0] == conf.User()
    s.alive[0] = False


def test_nameserver() -> None:
    s = Server()
    u = User( conf.get()['user']['name']
            , conf.get()['user']['group']
            , crypto.generate_keypair()[1]
            , [sock.get_extern_ip()]
            , conf.get()['user']['status'])
    s.register(u)
    print(len(s.users), 'users registered:')
    print(s.users)
    # TODO: test ask()
    s.alive[0] = False
    import time; time.sleep(1)
    import threading as th; assert th.active_count() == 1
    print('crypto.py: UNIT TESTS PASSED')



def test():
    test_crypto_sane()
    test_sockmock()
    test_send_recv_msg()
    test_send_recv_pubkey()
    test_send_recv_user()
    test_handshake()
    test_nameserver()

    print('protocol.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
