#!/usr/bin/env python3


'''
Socket stuff - provides connection objects.

All the usual
    - dropped messages
    - out of order messages
    - binary deviations in transit
    - weird endianness and padding
    - etc.
are the norm.

For some reason, even after socket.setblocking(True)
socket.recv() doesn't block.
time.sleep() is the current workaround.
'''


import requests
import socket
import threading
import time

import crypto
import pack
import port


MAX_MSG_BYTES=1024


def send( text: str
        , s: socket.socket
        , remote_pub: crypto.Pub
        , own_priv: crypto.Priv = crypto.read_keypair()[0]
        ) -> None:
    signature = crypto.sign(text, own_priv)
    encrypted = crypto.encrypt(text, remote_pub)
    msg = pack.Packet(encrypted, signature).to_bytes()
    for m in chop(msg):
        s.sendall(m)


def recv( s: socket.socket, alive: bool=True ) -> bytes:
    '''
    Accepts packets on a socket until terminated.
    '''
    while alive:
        data = s.recv(MAX_MSG_BYTES)

        # Ignore empty packets.
        if data:
            yield data

        # For some unfantomable reason
        # after the first connection is established (e.g. rat register)
        # CPU usage rises to 100% or even 200%.
        # The reason is that .recv() returns zero-length packets.
        # This is a workaround until the issue has been figured out.
        time.sleep(0.1)


def recv_one(s: socket.socket) -> bytes:
    '''Stitch any maximum size packet to the next one.'''
    alive = True
    ret = []
    for data in recv(s, alive):
        ret.append(data)
        if len(data) < MAX_MSG_BYTES:
            alive = False
            return stitch(ret)


def get_extern_ip() -> str:
    ip = requests.get('https://api.ipify.org').text
    return ip


class Server:
    '''
    Anticipate connections forever. Mind your firewall.

    A server TCP socket is always meant to negotiate connections, not content.
    Each returned connection is a content socket with a client.

    func(socket.socket) - communicate with one client until connection drops

    Set `me.alive = False` to kill permanently.
    '''


    MAX_THREADS = 20


    def __init__(me, port: int=0, func: callable=None):
        me.ip = get_extern_ip()
        me.port = port
        me.alive = True
        threading.Thread( target=me._listen
                        , args=[port, func]
                        , name='server'
                        ).start()
        print('Server listening on ip', me.ip, 'port', me.port)


    def _listen(me, port: int, func: callable) -> None:
        assert 0 <= port <= 2**16-1, port

        try:
            # Requires python > 3.7. Same for the client below.
            s = socket.create_server(('', port))
        except:
            s = socket.socket()
            s.bind(('localhost', port))

        s.listen()

        for conn, addr in me._live(s):
            print('New client connected:', addr)
            threading.Thread( target=func
                    , args=[conn]
                    , name='server'
                    ).start()

        print('Shutting down server on ip', me.ip, 'port', me.port)


    def _live(me, s: socket.socket) -> (socket.socket, tuple):
        '''
        Listens on a server socket, when a client connects, returns a client socket.
        Check every second for a server stop request.
        '''
        s.settimeout(1.0)

        while me.alive:
            try:
                conn, addr = s.accept()
                yield conn, addr
            except socket.timeout:
                pass


class Client:
    def __init__(me, ip: str, port: int, func: callable):
        try:
            s = socket.create_connection((ip, port))
        except:
            s = socket.socket()
            s.connect((ip, port))

        assert s
        func(s)



def test_chop_stitch():
    max = 42
    data = b'This is an extremely long text!' * 666
    packets = chop(data, max)
    assert stitch(packets) == data


def test_server_client() -> None:
    def listen(s):
        timeout = 20
        for data in recv(s):
            assert data and len(data)
            timeout -= 1
            if timeout == 0:
                return

    def yell(s):
        for i in range(0, 20):
            msg = 'This is the' + str(i) + 'th message!'
            s.sendall(msg.encode('utf8'))

    s = Server(port.CHATSERVER, listen)
    time.sleep(1)
    Client('localhost', port.CHATSERVER, yell)
    time.sleep(1)
    s.alive = False


def test() -> None:
    test_chop_stitch()
    test_server_client()
    print('sock.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
