#!/usr/bin/env python3


'''
A serverless chat client.
Refer to the README for dessign goals and usage.
'''


import socket


def create_server(port):
    '''
    Anticipate connections. Mind your firewall.
    '''
    s = socket.create_server(('', port))
    s.listen()
    conn, addr = s.accept()
    print('New connection from', addr)
    while True:
        data = conn.recv(1024)
        if data:
            print('READ:', data)


def create_client(ip, port):
    s = socket.create_connection((ip, port))
    for i in range(202):
        s.sendall(b'Heya')


def test():
    import socket
    import threading
    port = 42666

    threading.Thread(target=create_server
                    , args=[port]
                    , name='server'
                    ).start()

    threading.Thread(target=create_client
                    , args=['localhost', port]
                    , name='client'
                    ).start()


if __name__ == '__main__':
    test()
