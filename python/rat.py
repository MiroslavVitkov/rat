#!/usr/bin/env python3


'''
A peer to peer chat client/server/nameserver entry point.
'''


from threading import Thread
import sys
import time
import socket

import bot
import conf
import crypto
import protocol
import sock


def say( ip: str, text: str) -> None:
    '''
    Send a text message to someone listening and disconnect.
    Example: $rat say localhost hey bryh, wazzup
    '''
    own_priv, _ = crypto.read_keypair(conf.get_keypath())

    def func(s: socket):
        '''Transmit a message and die.'''
        remote = protocol.handshake_as_client(s)
        protocol.send_msg(text, s, own_priv, remote.pub)

    sock.Client(func, ip, conf.CHATSERVER)


def listen() -> None:
    '''
    Accept and display incoming messages.
    '''
    def forever(s: socket, a: [bool]):
        try:
            # Handshake.
            client = protocol.handshake_as_server(s)
            print('The remote user identifies as', client)

            # Accept messages.
            priv, _ = crypto.read_keypair()
            while True:
                msg = protocol.recv_msg(s, priv, client.pub, a)
                print(msg.decode('utf8'))
        except:
            # Drop the connection as soon as it breaks protocol.
            return

    sock.Server(forever, conf.CHATSERVER)


def relay() -> None:
    '''Chatroom.'''
    peers = set()

    def forever(s: socket, a: [bool]):
        try:
            # Handshake.
            client = protocol.handshake_as_server(s)
            peers.add(s)
            print('The remote user identifies as', client)

            # Relay messages.
            priv, _ = crypto.read_keypair()
            while True:
                msg = protocol.recv_msg(s, priv, client.pub, a)
                print(msg.decode('utf8'))
                for s_ in peers:
                    if s_ != s:
                        protocol.send_msg(msg, s_)
                #[protocol.send_msg(msg, s_) for s_ in peers if s_ != s]
        except:
            #peers.remove(s)
            # Drop the connection as soon as it breaks protocol.
            return

    sock.Server(forever, conf.CHATSERVER)


def ask(regex: str, ip: [str]) -> None:
    '''Request a list of matching userames from a nameserver.'''
    own_priv, _ = crypto.read_keypair()
    def f(s: socket):
        server = protocol.handshake_as_client(s)
        protocol.send_msg(regex, s, own_priv, server.pub)
        data = protocol.recv_msg(s, own_priv, server.pub)
        user = protocol.User.from_bytes(data)
        print(user)

    c = sock.Client(func=f, ip=ip[0], port=conf.NAMESERVER)


def register(ip: [str]) -> None:
    '''
    Register our User object(conf.ini + pub key) with nameserver(s).
    '''
    def func(s: socket):
        server = protocol.handshake_as_client(s)
        own_priv, _ = crypto.read_keypair()
        protocol.send_msg(b'register', s, own_priv, server.pub)

    sock.Client(ip=ip[0], port=conf.NAMESERVER, func=func)


def serve() -> None:
    '''
    Run a nameserver forever.
    On the standard port.
    Acept all requests from everyone.
    '''
    protocol.NameServer()


def get_prompt( name: str=conf.get()['user']['name']
              , group:str=conf.get()['user']['group']
              ) -> str:
    return (name + '@' + group + '<-')


def test() -> None:
    # An `os.listdir('.')` wouldn't allow us to selectively disable tests.
    bot.test()
    conf.test()
    crypto.test()
    protocol.test(); time.sleep(1)
    sock.test()

    # System test.
    try:
        Thread(target=listen, daemon=True).start()
        Thread(target=connect, args=['localhost'], daemon=True).start()
# TODO: actually send a mesage and validate it was received
        print('\nSYSTEM TEST PASSED')
    except Exception as e:
        print('\nSYSTEM TEST FAILED!')
        print('Reason: ', e)


def print_help() -> None:
    h = '''
        Usage:

        resolving users
        ---
            rat serve - start a nameserver
            rat register <ip1>...<ip n> - publish details to nameserver(s)
            rat ask <regex> <ip1>...<ip_n>  - ask nameservers for user details by regex

        chatting
        ---
            rat listen - accept incoming chats, interactively
            rat relay - start a chatroom
            rat connect <ip> - start chatting if they are listening, interactively
            rat send <ip> <msg> - send a message and shut down
            rat get [<ip>] - read accumulated messages and shut down

        miscellaneous
        ---
            rat generate - create a new RSA keypair and write it to disk
            rat test - run all unnit and integration tests
            rat help - print this message
        '''
    print(h)


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'help' or sys.argv[1] == '?':
        print_help()

    # Example: rat say localhost Hey bryh!
    elif sys.argv[1] == 'say':
        if len(sys.argv) > 3:
            msg = ' '.join(sys.argv[3:])
            say(sys.argv[2], msg)
        else:
            print('Provide a destination IP and a message!')

    elif sys.argv[1] == 'listen':
        listen()

    elif sys.argv[1] == 'relay':
        relay()

    # Example: rat ask regex server1 server2
    elif sys.argv[1] == 'ask':
        if len(sys.argv) >= 4:
            ask(sys.argv[2], sys.argv[3:])
        else:
            print('Provide your regex followed by nameserver IPs!')

    # Example: rat register server1 server2
    elif sys.argv[1] == 'register':
        if len(sys.argv) >= 3:
            register(sys.argv[2:])
        else:
            print('Provide the IPs of the nameservers!')

    elif sys.argv[1] == 'serve':
        serve()

    elif sys.argv[1] == 'generate':
        assert len(sys.argv) == 2
        keypath = conf.get_keypath()
        priv, pub = crypto.generate_keypair()
        crypto.write_keypair(priv, pub, keypath)

    elif sys.argv[1] == 'test':
        test()

    else:
        print(sys.argv[1], '- command not recognised')
        print_help()
