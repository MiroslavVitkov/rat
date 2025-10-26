#!/usr/bin/env python3


'''
Nameserver i.e. a phonebook.
'''


from socket import socket
from threading import Event
from typing import Self

import pickle
import re
import time

from impl import conf
from impl import crypto
from impl import sock

from prot.chat import send_msg, recv_msg
#from prot import handshake


class User:
    '''
    A 'user' is defined by their public key.
    Meaning that 5 devices with the same key are one logical user.
    '''


    def __init__( me
                , name: str=conf.get()['about']['name']
                , group: str=conf.get()['about']['group']
                , pub: crypto.Pub=crypto.read_keypair()[1]
                , status: str=conf.get()['about']['status']
                , ip: str=conf.get()['about']['ip']
                ):
        me.name = name
        me.group = group
        me.pub = pub
        me.ip = ip
        me.status = status


    @classmethod
    def from_bytes(cls, b: bytes) -> Self:
        obj = pickle.loads(b)
        assert type(obj) == cls, (type(obj), cls)
        return obj


    def to_bytes(me) -> bytes:
        return pickle.dumps(me)


    def __repr__(me) -> str:
        assert(me)
        assert(me.pub)
        pub = str(me.pub.save_pkcs1())
        return ( '\n'
               + 'nickname: ' + me.name + '\n'
               + 'group: ' + me.group + '\n'
               + 'public key: ' + pub + '\n'
               + 'IP: ' + me.ip + '\n'
               + 'status: ' + me.status)


    def __eq__(me, other):
        if type(me) != type(other):
            return False;
        return me.__dict__ == other.__dict__


    def __hash__(me) -> int:
        return hash(repr(me))


class Server:
    '''
    A phonebook.
    '''
    def __init__(me):
        me.users = {}
        me.death = Event()

        me.server = sock.Server(me._handle, conf.NAMESERVER)
        me.server.death = me.death
        me.priv, _ = crypto.read_keypair()


    def register(me, u: User) -> None:
        assert type(u) == User, type(u)
        me.users[u.pub] = u
        print('New user registered:', u)
        print('Now there are', len(me.users), 'registered users.\n')


    def ask(me, regex) ->[bytes]:
        try:
            r = re.compile(regex)
        except:
            send_msg(b'Invalid regular expression!', s, own_priv, remote_pub)
            return []

        r = [u.to_bytes() for u in me.users.values()
             if r.match(u.name)]
        return r


    def _handle(me, s: socket, death: Event) -> None:
        try:
            # A global import causes cirtular dependency.
            from prot.handshake import as_server
            client = as_server(s)
            print(client)
        except:
            # Drop the connection as soon as it breaks protocol.
            return

        # We expect exacly one text message from this peer.
        # After that we disconnect by returning from this handler.
        priv, _ = crypto.read_keypair()
        try:
            msg = recv_msg(s, priv, client.pub)
            if msg == b'register':
                me.register(client)
            else:
                msg = msg.decode('utf8')
                print(s.getsockname(), 'is asking for', msg)
                for u in me.ask(msg):
                    send_msg(u, s, priv, client.pub)
        except:
            pass


def send_user( s: socket
             , remote_pub: crypto.Pub ) -> None:
    own_priv, _ = crypto.read_keypair()
    u = User().to_bytes()  # 282 bytes
    send_msg(u, s, own_priv, remote_pub)


def recv_user( s: socket, remote_pub: crypto.Pub ) -> User:
    '''
    Receive remote User object encrypted and signed.
    A copy-ast of recv_msg() which however allows None.
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


def test_send_recv_user() -> None:
    '''Exchange user objects having reliably exchanged public keys.'''
    _, pub = crypto.read_keypair()
    received = []
    server = sock.Server(lambda s, _: received.append(recv_user(s, pub)))
    sock.Client(lambda s: send_user(s, pub))

    time.sleep(1)
    assert received[0] == User(), received[0]
    server.death.set()
    time.sleep(sock.POLL_PERIOD)


def test_nameserver() -> None:
    s = Server()
    u = User()
    s.register(u)
    assert len(s.users) == 1, len(s.users)
    assert s.ask(u.name)[0] == u.to_bytes(), len(s.ask(u.name))
    assert s.ask('.*')[0] == u.to_bytes(), len(s.ask('*'))
    s.death.set()
    time.sleep(sock.POLL_PERIOD)


def test():
    test_send_recv_user()
    test_nameserver()
    assert User.from_bytes(User().to_bytes()) == User()

    print('prot/name.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
