#!/usr/bin/env python3


'''
A server where users publish their (nickname, public key, ip, comment)
for everyone to see.

Groups look like regular users but are based on peer to peer broadcast.
Still a central relay ca be created easily.

Encryption is cool but no authentication mechanism has been implemented yet!
'''


import pickle
import re
import socket
import time

import conf
import crypto
import port
from sock import MAX_MSG_BYTES
import sock


class User:
    '''
    '''
    def __init__( me
                , name: str
                , pub: crypto.Pub
                , ip: [str]
                , status: str=''
                ):
        me.name = name
        me.pub = pub
        me.ip = ip
        me.status = status


    @classmethod
    def from_bytes(cls, b: bytes):
        obj = pickle.loads(b)
        assert(type(obj) == cls)
        return obj


    def to_bytes(me) -> bytes:
        b = pickle.dumps(me)
        assert(len(b) < MAX_MSG_BYTES)
        return b


    def __repr__(me):
        pub = str(me.pub.save_pkcs1())
        return ( '\n'
               + 'nickname: ' + me.name + '\n'
               + 'public key: ' + pub + '\n'
               + 'IP: ' + me.ip + '\n'
               + 'status: ' + me.status)


def handshake(s: socket.socket) -> User:
    '''
    The client has obtained the server's ip and public key via another medium.
    They initiate a connection on port.CHATSERVER.
    The server and the client open a socket each.
    Those last until closed by one side.
    '''
    while True:
        data = s.recv(1024)
        if data:
            remote_user = pickle.loads(data)
            assert(type(remote_user) == type(User))
            return remote_user
        else:
            time.sleep(0.2)


class Server:
    '''
    The client has obtained the nameserver's ip and public key via another medium.
    '''
    def __init__(me):
        me.users = {}
        me.server = sock.Server(port.NAMESERVER, me._handle)
        me.server.alive = True


    def register(me, u: User):
        assert(type(u) == User)
        me.users[u.pub] = u


    def _handle(me, s: socket.socket):
        while me.alive:
            me.server.alive = me.alive
            try:
                data = s.recv(1024)
            except:
                # Perhaps the user disconnected.
                pass
            if data:
                # This could be an `ask` or a `register` request.
                try:
                    remote_user = User.from_bytes(data)
                    assert(type(remote_user) == User)
                    me.register(remote_user)
                    print('New user registered:', remote_user)
                    print('Now there are', len(me.users), 'registered users.\n')
                except:
                    regex = data.decode('utf-8')
                    print(s.getsockname(), 'is asking for', regex)
                    r = re.compile(regex)
                    matches = [me.users[u] for u in me.users
                               if r.match(me.users[u].name)]
                    for u in matches:
                        try:
                            bytes = pickle.dumps(u)
                            s.sendall(bytes)
                        except:
                            # Perhaps the user disconnected?
                            continue
                    continue


def test():
    s = Server()
    u = User( conf.get()['user']['name']
            , crypto.read_keypair()[1]
            , sock.Server(port.NAMESERVER+4, None).ip
            , conf.get()['user']['status'])
    s.register(u)
    print(s.users)
    s.alive = False
    s.server.alive = False
    print('crypto.py: ALL TESTS PASSED')


if __name__ == "__main__":
    test()
