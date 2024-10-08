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
        Gets transmitted around thus contains everything but the private key.
    '''
    U = conf.get()['user']


    def __init__( me
                , name: str=U['name']
                , group: str=U['group']
                , pub: crypto.Pub=crypto.read_keypair()[1]
                , ips: [str]=[sock.get_extern_ip(),]
                , status: str=U['status']
                ):
        me.name = name
        me.group = group
        me.pub = pub
        me.ips = ips
        me.status = status


    @classmethod
    def from_bytes(cls, b: bytes) -> 'User':
        obj = pickle.loads(b)
        assert type(obj) == cls, (type(obj), cls)
        return obj


    def to_bytes(me) -> bytes:
        return pickle.dumps(me)


    def __repr__(me) -> str:
        assert(me)
        assert(me.pub)
        pub = str(me.pub.save_pkcs1())
        ips = ', '.join(me.ips)
        return ( '\n'
               + 'nickname: ' + me.name + '\n'
               + 'group: ' + me.group + '\n'
               + 'public key: ' + pub + '\n'
               + 'IPs: ' + ips + '\n'
               + 'status: ' + me.status)

    def __eq__(me, other):
        if type(me) != type(other):
            return False;
        return me.__dict__ == other.__dict__


class Server:
    '''
    The client has obtained the nameserver's ip and public key via another medium.
    '''
    def __init__(me):
        me.users = {}
        me.alive = [True]

        me.server = sock.Server(port.NAMESERVER, me._handle)
        me.server.alive = me.alive
        me.priv, _ = crypto.read_keypair()


    def register(me, u: User) -> None:
        assert type(u) == User, type(u)
        me.users[u.pub] = u


    def _handle(me, s: socket.socket) -> None:
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


def test() -> None:
    assert User.from_bytes(User().to_bytes()) == User()

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


if __name__ == "__main__":
    test()
