#!/usr/bin/env python3


'''
A server where users publish their (username, public key, ip)
for everyone to see.

Groups look like regular users, but are based on peer to peer broadcast.

Encryption is cool but no authentication mechanism has been implemented yet!
'''


import time

import crypto
import pack
import rat
import sock


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


if __name__ == "__main__":
    s = sock.Server(rat.PORT, func)
