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

import conf
import crypto
import port
import sock


class User:
    '''
        Gets transmitted around thus contains everything but the pruvate key.
    '''
    U = conf.get()['user']


    def __init__( me
                , name: str=U['name']
                , group: str=U['group']
                , pub: crypto.Pub=crypto.read_keypair()[1]
                , ip: [str]=[sock.get_extern_ip(),]
                , status: str=U['status']
                ):
        me.name = name
        me.group = group
        me.pub = pub
        me.ip = ip
        me.status = status


    @classmethod
    def from_bytes(cls, b: bytes) -> 'User':
        obj = pickle.loads(b)
        assert type(obj) == cls, (type(obj), cls)
        return obj


    def to_bytes(me) -> bytes:
        b = pickle.dumps(me)
        assert len(b) < sock.MAX_MSG_BYTES, len(b)
        return b


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


class Server:
    '''
    The client has obtained the nameserver's ip and public key via another medium.
    '''
    def __init__(me):
        me.users = {}
        me.server = sock.Server(port.NAMESERVER, me._handle)
        me.alive = True


    def register(me, u: User) -> None:
        assert type(u) == User, type(u)
        me.users[u.pub] = u


    def _handle(me, s: socket.socket) -> None:
        own_priv, _ = crypto.read_keypair()

        for data in sock.recv(s, me.alive):
          # Accept remote User object.
            remote_user = User.from_bytes(data)
            assert type(remote_user) == User, type(remote_user)

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
                    sock.send( b'Invalid regular expression!'
                             , s, own_priv, remote_pub )
                    continue

                matches = [me.users[u] for u in me.users
                           if r.match(me.users[u].name)]
                if not matches:
                    sock.send( b'No matches!'
                             , s, own_priv, remote_user.pub )
                    continue

                for u in matches:
                    bytes = pickle.dumps(u)
                    sock.send(bytes, s, own_priv, remote_user.pub)

            me.server.alive = me.alive  # Kill the parent server.


def test() -> None:
    s = Server()
    u = User( conf.get()['user']['name']
            , conf.get()['user']['group']
            , crypto.generate_keypair()[1]
            , sock.get_extern_ip()
            , conf.get()['user']['status'])
    s.register(u)
    print(s.users)
    s.alive = False
    print('crypto.py: ALL TESTS PASSED')


if __name__ == "__main__":
    test()
