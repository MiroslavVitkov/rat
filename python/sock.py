#!/usr/bin/env python3


'''
Provides TCP/IP connection objects, perhaps soon UDP too.
'''


import socket
import threading
import time

import conf
from crypto import CHUNK_BYTES


def recv( s: socket.socket
        , alive: [bool]=[True]
        , _cache: [bytes]=[b''] ) -> bytes:
    '''
    Block until one chunk is yielded.
    Use 'alive' to kill from the outside.
    Returns(doesn't throw) on remote disconnect.
    '''
    # Index 0 of the buffer is the oldest received chunk.
    def try_yield():
        while len(_cache[0]) >= CHUNK_BYTES:
            r = _cache[0][:CHUNK_BYTES]
            _cache[0] = _cache[0][CHUNK_BYTES:]
            yield r

    yield from try_yield()

    s.settimeout(.1)
    while alive[0]:
        try:
            # Recommended value in the docs.
            data = s.recv(4096)

            _cache[0] += data  # Larger index means more recent data.
            yield from try_yield()

            # The client has disconnected.
            if not data:
                assert len(_cache[0]) == 0, (len(_cache[0]), _cache[0])
                return  # == raise StopIteration

        except socket.timeout:
            pass
        except ConnectionResetError:  # Probably the client disconnected.
            assert len(_cache[0]) == 0, (len(_cache[0]), _cache[0])
            return  # == raise StopIteration


def recv_one(s: socket, a: [bool]=[True]):
    return next(iter(recv(s, a)))


class Server:
    '''
    Anticipate connections forever. Mind your firewall.

    A server TCP socket is always meant to negotiate connections, not content.
    Each returned connection is a content socket with a client.

    func(socket, [alive]) - communicate with one client until connection drops

    Set `me.alive[0] = False` to kill permanently but spawned children remain unaffected.
    '''


    MAX_THREADS = 20


    def __init__(me, func: callable, port: int=conf.TEST):
        me.ip = conf.get_extern_ip()
        me.port = port
        me.alive = [True]
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
            threading.Thread( target=func
                            , args=[conn, me.alive]
                            , name='server_content_socket'
                            ).start()

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
    def __init__(me, func: callable, ip: str='localhost', port: int=conf.TEST):
        try:
            s = socket.create_connection((ip, port))
        except:
            s = socket.socket()
            s.connect((ip, port))

        func(s)


def test_nonblocking_recv() -> None:
    '''
    Make sure recv() can be terminated while there's nothing to be read on the socket.
    '''
    # Create 3 sockets - sever administrative, server content and client content.
    # Bind the latter and forget about the former.
    server_s = socket.create_server(('', conf.TEST))
    server_s.listen()
    client_s = socket.create_connection(('localhost', conf.TEST))
    content_s = next(iter(server_s.accept()))  # Accept 1 connection.

    client_s.sendall('If this is commented out, the server hangs.'.encode('utf8'))

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
        while alive[0]:
            print(s.recv(1024))
    def yell(s: socket):
        '''Client transmits something and disconnects.'''
        s.sendall('Something!'.encode('utf8'))
    s = Server(listen)
    Client(yell)

    # Kill the server.
    # The child connection notices that through it's bool parameter and commits suicide.
    # Manual regression test here: time.sleep() and check cpu usage.
    s.alive[0] = False
    time.sleep(1)
    assert threading.active_count() == 1


def test_recv() -> None:
    '''
    Ensure packets are received in the correct chunk, byte and bit order.
    Not much to test about send() - all the logic is external.
    '''
    def listen(s: socket, alive: [bool]=[True]):
        for msg in recv(s, alive):
            print(msg[0], end=', ')

    def say(s):
        m = bytearray(b'.') * CHUNK_BYTES
        for i in range(20):
            m[0] = i
            s.sendall(m)

    server = Server(listen)
    client = Client(say)
    time.sleep(1)
    server.alive[0] = False
    print('20')  # For the newline.


def test() -> None:
    test_nonblocking_recv()
    test_server_client()
    test_recv()
    print('sock.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
