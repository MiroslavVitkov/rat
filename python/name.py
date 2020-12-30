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

import crypto
import port
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
        assert(len(b) < 1024)
        return b


    def __repr__(me):
        pub = str(me.pub.save_pkcs1())
        return ( '\n'
               + 'User: ' + me.name + '\n'
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
            assert(len(data) < 1024)
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
        me.users = set()
        me.server = sock.Server(port.NAMESERVER, me._handle)


    def register(me, u:User):
        me.users.add(u)


    def _handle(me, s: socket.socket):
        while True:
            try:
                data = s.recv(1024)
            except:
                # Perhaps the user disconnected.
                pass
            if data:
                assert(len(data) < 1024)

                # This could be an `ask` or a `register` request.
                try:
                    remote_user = User.from_bytes(data)
                    assert(type(remote_user) == User)
                    print('MNOGOLAINA')
                    me.register(remote_user)
                    print('New user registered:', remote_user)
                    print('Now there are', len(me.users), 'registered users.')
                except:
                    regex = data.decode('utf-8')
                    print(s.getsockname(), 'is asking for', regex)
                    r = re.compile(regex)
                    matches = [pickle.dumps(u) for u in me.users if r.match(u.name)]
                    for u in matches:
                        try:
                            s.sendall(u)
                        except:
                            # Perhaps the user disconnected?
                            continue
                    continue





import pack
import rat
import sock


            #remote_pub = crypto.Pub.load_pkcs1(data)
            #s.sendall(own_pub.save_pkcs1())

own_priv, own_pub = crypto.generate_keypair()







def anticipate(s: sock.socket.socket, remote_pub: crypto.Pub) -> None:
    while True:                                                         
        data = s.recv(1024)                                             
        if data:                                                        
            packet = pack.Packet.from_bytes(data)                       
            text = crypto.decrypt(packet.encrypted, own_priv)
            crypto.verify(text, packet.signature, remote_pub)           
            print(text)                                                 
        time.sleep(0.1)




def func(s: sock.socket.socket) -> crypto.Pub:
    remote_pub = rat.handshake(s, own_pub)
    rat.handle_input(s, own_priv, remote_pub)
    anticipate(s, remote_pub)


def test():
    s = Server(rat.PORT+1, func)
    u = User('miro', own_pub,'localhost','suffering')
    s.add(u)
    print(s)


if __name__ == "__main__":
    test()
