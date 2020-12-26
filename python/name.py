#!/usr/bin/env python3


'''
A server where users publish their (nickname, public key, ip, comment)
for everyone to see.

Groups look like regular users but are based on peer to peer broadcast.
Still a central relay ca be created easily.

Encryption is cool but no authentication mechanism has been implemented yet!
'''


import pickle
import socket
import time

import crypto
import ports
import sock


# tuple(nickname, key, ip, public comment)
User = (str, crypto.Pub, str, status)
Group = (str, crypto.Pub, [str], status)


def handshake(s: socket.socket) -> User:
    '''
    The client has obtained the server's ip and public key via another medium.
    They initiate a connection on ports.CHATSERVER.
    The server and the client open a socket each.
    Those last until closed by one side.
    '''
    while True:
        data = s.recv(1024)
        if data:
            assert(len(data) < 1024)

            remote_user = pickle.loads(data)
            assert(type(remote_user) is User)

            return remote_user
        else:
            time.sleep(0.2)


class Server:
    '''
    The client has obtained the nameserver's ip and public key via another medium.
    
    
    '''
    def __init__(me):
        me.users = set()
        me.server = sock.Server(port, handshake)


    def register(me, u:User):
        me.users.add(u)


    def deregister(me, u:User):
        me.users.add(u)







import pack
import rat
import sock


            #remote_pub = crypto.Pub.load_pkcs1(data)
            #s.sendall(own_pub.save_pkcs1())

own_priv, own_pub = crypto.generate_keypair()



class User2:
    '''
    A user has a single IP value, a group has multiple.
    Should probably just be a tuple.
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
        return onj


    def to_bytes(me) -> bytes:
        b = picle.dumps()
        assert(len(b) < 1024)
        return b


    def __repr__(me):
        return 'NA NIVATA'




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
