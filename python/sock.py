#!/usr/bin/env python3


'''
Socket stuff - provides connection objects.
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
    for m in crypto.chop(msg):
        s.sendall(m)


def recv( s: socket.socket, alive: [bool]=[True] ) -> bytes:
    '''
    Accepts packets on a socket until terminated or the remote leaves.
    '''
    s.settimeout(.1)

    while alive[0]:
        try:
            data = s.recv(MAX_MSG_BYTES)

            # A returned empty bytes object indicates that the client has disconnected.
            if not data:
                return  # == raise StopIteration

            yield data
        except socket.timeout as e:
            pass


def recv_one(s: socket.socket) -> bytes:
    '''
    Block until a single message has been received and read out.

    Stitching long messages is a TODO.
    '''
    for data in recv(s):
        assert len(data) <= MAX_MSG_BYTES, len(data)
        return data


def get_extern_ip() -> str:
    ip = requests.get('https://api.ipify.org').text
    return ip


class Server:
    '''
    Anticipate connections forever. Mind your firewall.

    A server TCP socket is always meant to negotiate connections, not content.
    Each returned connection is a content socket with a client.

    func(socket, [alive]) - communicate with one client until connection drops

    Set `me.alive[0] = False` to kill permanently but spawned children remain unaffected.
    '''


    MAX_THREADS = 20


    def __init__(me, port: int=0, func: callable=None):
        me.ip = get_extern_ip()
        me.port = port
        me.alive = [True]
        me.children = []
        me.thread = threading.Thread( target=me._listen
                                    , args=[port, func]
                                    , name='server'
                                    )
        me.thread.start()
        print('Server listening on ip', me.ip, 'port', me.port)


    def _listen(me, port: int, func: callable) -> None:
        '''
        Accept connections and create a thread with the passed callback for each.
        '''
        assert 0 <= port <= 2**16-1, port

        try:
            # Requires python > 3.7. Same for the client below.
            s = socket.create_server(('', port))
        except:
            s = socket.socket()
            s.bind(('localhost', port))

        s.settimeout(.1)
        s.listen()

        for conn, addr in me._poll(s):
            print('New client connected:', addr)
            me.children.append( threading.Thread( target=func
                                                , args=[conn, me.alive]
                                                , name='server_content_socket'
                                                ) )
            me.children[-1].start()


        # Close listener socket - already established connections are unaffected.
        s.close()
        print('Server down on ip', me.ip, 'port', me.port)


    def _poll(me, s: socket):
        while me.alive[0]:
            try:
                conn, addr = s.accept()
                yield conn, addr
            except socket.timeout:
                pass


class Client:
    '''
    Client-side view of the pipe to the Server over the assigned socket.
    '''
    def __init__(me, ip: str, port: int, func: callable):
        try:
            s = socket.create_connection((ip, port))
        except:
            s = socket.socket()
            s.connect((ip, port))

        assert s
        func(s)


def test_nonblocking_recv() -> None:
    '''
    Make sure recv() can be terminated while there's nothing to be read on the socket.
    '''
    # Create 3 sockets - sever administrative, server content and client content.
    # Bind the latter and forget about the former.
    server_s = socket.create_server(('', port.TEST))
    server_s.listen()
    client_s = socket.create_connection(('localhost', port.TEST))
    content_s = next(iter(server_s.accept()))  # Accept 1 connection.

    # client_s.sendall('If this is commented out, the server hangs.'.encode('utf8'))

    alive = [True]
    def read_one_message():
        data = recv(content_s, alive)
        # print(next(iter(data)))  # This fails if nothing was sent.

    content_th = threading.Thread(target=read_one_message, name='content_th')
    content_th.start()
    time.sleep(1)
    alive[0] = False
    content_th.join()
    assert threading.active_count() == 1


def test_server_client() -> None:
    '''
    This is the intended API of the module.
    '''
    def listen(s: socket, alive: [bool]=[True]):
        '''Server echoes received strings, forever.'''
        for msg in recv(s, alive):
            print(msg)
        print('Listener disonnected or killed.')
    def yell(s: socket):
        '''Client transmits something and disconnects.'''
        s.sendall('Something!'.encode('utf8'))
    s = Server(port.TEST, listen)
    Client('localhost', port.TEST, yell)

    # Kill the server.
    # The child connection notices that through it's bool parameter and commits suicide.
    # Manual regression test here: time.sleep() and check cpu usage.
    s.alive[0] = False
    time.sleep(1)
    assert threading.active_count() == 1


def test() -> None:
    test_nonblocking_recv()
    test_server_client()
    print('sock.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
