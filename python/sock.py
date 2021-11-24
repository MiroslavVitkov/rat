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


from concurrent.futures import ThreadPoolExecutor
import requests
import socket
import threading
import time


class Server:
    '''
    Anticipate connections forever. Mind your firewall.

    A server TCP socket is always meant to negotiate connections, not content.  
    Each returned connection is a content socket with a client.

    func(socket.socket) - communicate with one client until connection drops

    Set `me.alive = False` to kill permanently.
    '''


    MAX_THREADS = 20


    def __init__(me, port: int, func: callable):
        me.ip = me._get_extern_ip()
        me.port = port
        me.alive = True
        threading.Thread( target=me._listen
                        , args=[port, func]
                        , name='server'
                        ).start()
        print('Server listening on ip', me.ip, 'port', me.port)


    def _listen(me, port: int, func: callable):
        assert(port >= 0 and port <= 2**16-1)

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
            except socket.timeout as e:
                pass


    def _get_extern_ip(me):
        ip = requests.get('https://api.ipify.org').text
        return ip


class Client:
    def __init__(me, ip: str, port: int, func: callable):
        try:
            s = socket.create_connection((ip, port))
        except:
            s = socket.socket()
            s.connect((ip, port))

        assert(s)
        func(s)


def test():
    port = 42666

    # Thread handlers are difficult to write.
    # It would be nice to incorporate most of the complexity into the class.
    def listen(s):
        timeout = 20
        while True:
            time.sleep(0.1)
            d = s.recv(1024)
            if d:
                print('received', len(d), 'bytes:', d)
                timeout += 20
            timeout -= 1
            if timeout == 0:
                return

    def yell(s):
        for i in range(0, 20):
            msg = 'This is the' + str(i) + 'th message!'
            s.sendall(msg.encode('utf8'))

    port = 42666
    s = Server(port, listen)
    import time
    time.sleep(1)
    c = Client('localhost', port, yell)
    time.sleep(1)
    s.alive = False


if __name__ == '__main__':
    test()
