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


import socket
import threading
import time

from concurrent.futures import ThreadPoolExecutor


class Server:
    '''
    Anticipate connections forever. Mind your firewall.                         
                                                                                 
    A server TCP socket is always meant to negotiate connections, not content.  
    Each returned connection is a content communication port with a client.     

    func(socket.socket) - communicate with one client until connection drops
    '''


    MAX_THREADS = 20


    def __init__(me, port: int, func: callable):
        '''func(socket.socket) - handle that client forever'''
        assert(port >= 0 and port <= 2**16-1)
        s = socket.create_server(('', port))
        s.listen()
        with ThreadPoolExecutor(max_workers=me.MAX_THREADS) as t:
            while True:
                conn, addr = s.accept()    # conn - socket.socket to a peer
                print('New client connected:', addr)
                t.map(func, [conn])
                if True:
                    return
                time.sleep(0.1)

class Client:
    def __init__(me, ip: str, port: int, func: callable):
        s = socket.create_connection((ip, port))
        func(s)


def test():
    port = 42666

    # Thread handlers are hard to write.
    # It would be nice to incorporate most of the complexity into the class.
    def listen(s):
        timeout = 0
        while True:
            time.sleep(0.1)
            d = s.recv(1024)
            if d:
                print('received', len(d), 'bytes:', d)
            timeout += 1
            if timeout > 20:
                return

    def yell(s):
        for i in range(0, 20):
            msg = 'This is the' + str(i) + 'th message!'
            s.sendall(msg.encode('utf8'))

    # Internally starts a new thread per client.
    ts = threading.Thread(target=Server
                         , args=[port, listen]
                         , name='server'
                         )
    tc0 = threading.Thread(target=Client
                          , args=['localhost', port, yell]
                          , name='client0'
                          )
    tc1 = threading.Thread(target=Client
                          , args=['localhost', port, yell]
                          , name='client1'
                          )

    ts.start()
    tc0.start()
    tc1.start()
    tc0.join()
    tc1.join()
    ts.join()


if __name__ == '__main__':
    test()
