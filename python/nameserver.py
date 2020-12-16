#!/usr/bin/env python3


'''
A server where users publish their (username, public key, ip)
for everyone to see.

Groups look like regular users but are based on peer to peer broadcast.

Encryption is cool but no authentication mechanism has been implemented yet!
'''


import time

import crypto
import pack
import rat
import sock


own_priv, own_pub = crypto.generate_keypair()


class User:
    '''
    A user has a single IP value, a group has multiple.
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


class Server:
    def __init__(me):
        me.users = set()
        me.server = sock.Server(port, func)


    def add(me, conn):
        # It's accepting registrations from anyone anyway.
        name = 'miro'
        pub = own_pub
        ip = 'localhost'
        status = 'suffering'
        u = User(name, pub , ip, status)


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
