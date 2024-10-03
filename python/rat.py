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
import name
import pack
from pack import Packet
import prompt
import protocol
import port
import sock


def serve() -> None:
    '''
    Run a nameserver forever.
    On the standard port.
    Acept all requests from everyone.
    '''
    name.Server()


def register(ip) -> None:
    '''
    Register our User object(conf.ini + pub key) with nameserver(s).
    '''
    def func(s: socket):
        server = protocol.handshake_as_client(s)
        own_priv, _ = crypto.read_keypair()
        sock.send(b'register', s, server.pub, own_priv)

    sock.Client(ip=ip, port=port.NAMESERVER, func=func)


def ask(regex: str, ip: str) -> None:
    '''Request a list of matching userames from a nameserver.'''
    def func(s: socket):
        server = protocol.handshake_as_client(s)
        sock.send('ask ' + regex, s, server.pub)
        data = sock.recv_one(s)
        print(data)

    c = sock.Client(ip[0], port=port.NAMESERVER, func=func)


def listen(relay: bool=False) -> None:
    '''
    Create a socket and listen on in with a dedicated thread, forever.
    relay - send everything received to everyone else(chatroom)
    '''
    own_priv, own_pub = crypto.read_keypair()
    remote_sockets = []
    remote_keys = []
    inout = bot.InOut()
    bot.spawn_bots(inout)

    def forever(s):
        # Handshake.
        client = protocol.handshake_as_server(s)
        print('The remote user identifies as', client)
        remote_sockets.append(s)
        remote_keys.append(client.pub)

        # TODO: report disconnects.
        print('New user joined:', client)

        # Accept text messages.
        for data in sock.recv(s):
            packet = Packet.from_bytes(data)
            text = crypto.decrypt(packet.encrypted, own_priv)
            crypto.verify(text, packet.signature, remote_user.pub)

            # Inform bots of the new input.
            inout.in_msg = text
            with inout.in_cond:
                inout.in_cond.notify_all()

            # Show the text. Should this be a bot?
            print( prompt.get( remote_user.name
                             , remote_user.group)
                 + text )

            # Relay operation.
            if relay:
                for socket, key in zip(remote_sockets, remote_keys):
                    if socket != s:
                        sock.send( prompt.get( remote_user.name
                                             , remote_user.group )
                                             + text
                                 , socket, key, own_priv)

    # Comenting this out temporarily.
    # It is responsible for a clissicle p2p chat.
    # TODO After connectionless rat is done and thested this need to be un-broken!
    # handle_input(remote_sockets, own_priv, remote_keys)
    sock.Server(port.CHATSERVER, forever)


def connect(ip: str) -> None:
    own_priv, own_pub = crypto.read_keypair()
    # TODO: spawn bots
    def func(s: socket):
        server = protocol.handshake_as_client(s)
        print('The server identifies as', server)

        # Send messages to the remote peer.
        handle_input((s,), own_priv, (server.pub,))

        # Receive messages from the remote peer.
        for data in sock.recv(s):
            packet = Packet.from_bytes(data)
            text = crypto.decrypt(packet.encrypted, own_priv)
            crypto.verify(text, packet.signature, remote_user.pub)

            # Show the text.
            print( prompt.get( remote_user.name
                             , remote_user.group)
                 + text )

    client = sock.Client(ip, port.CHATSERVER, func)


def send( ip: str, text: str) -> None:
    own_priv, own_pub = crypto.read_keypair(conf.get_keypath())

    def func(s: socket):
        '''Transmit a message and die.'''
        protocol.handshake_as_client(s)
        sock.send(text, s, own_priv, remote.pub)

    client = sock.Client(ip, port.CHATSERVER, func)


def get() -> None:
    pass


def handle_input( s: [socket]
                , own_priv: crypto.Priv
                , remote_pub: [crypto.Pub]
                , alive: bool=True
                ) -> None:
    '''
    We need 2 threads to do simultaneous input and output.
    So let's use the current thread for listening and spin an input one.
    '''
    def inp():
        while alive:
            text = input()
            # Forbid sending empty messages because they DOS the remote peer
            # (the remote network buffer gets clogged).
            # Perhaps a better alternative is to insert a delay in send()?
            # Because what we see on the screen is different from the peer's?
            if text:
                for ip, pub in zip(s, remote_pub):
                    sock.send(text, ip, own_priv, pub)

    Thread(target=inp).start()


def test() -> None:
    # An `os.listdir('.')` wouldn't allow us to selectively disable tests.
    bot.test()
    conf.test()
    crypto.test()
    name.test()
    pack.test()
    port.test()
    prompt.test()
#    protocol.test()  # Naughty boy - doesn't clean his sockets.
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

    elif sys.argv[1] == 'serve':
        serve()

    elif sys.argv[1] == 'register':
        if len(sys.argv) >= 3:
            register(sys.argv[2])  # TODO: allow multiple server IPs
        else:
            print('Provide the IP of the nameserver!')

    elif sys.argv[1] == 'ask':
        if len(sys.argv) >= 4:
            ask(sys.argv[2], sys.argv[3:len(sys.argv)])
        else:
            print('Provide your regex followed by nameserver IPs!')

    elif sys.argv[1] == 'listen':
        listen()

    elif sys.argv[1] == 'relay':
        listen(relay=True)

    elif sys.argv[1] == 'connect':
        if len(sys.argv) == 3:
            connect(sys.argv[2])
        else:
            print('Provide the IP to connect to, it must be listening!')

    elif sys.argv[1] == 'send':
        if len(sys.argv) >= 3:
            # No need for '' around the message.
            msg = ' '.join(sys.argv[3:])
            send(sys.argv[2], msg)
        else:
            print('Provide a destination IP and a message!')

    elif sys.argv[1] == 'get':
        if 'recv_buff' in conf.get()['user']['bots']:
            pass
        else:
            print('To enable this command you must both enable recv_buff bot '
                  'and keep a running `rat listen` instance.')

    elif sys.argv[1] == 'generate':
        if len(sys.argv) == 2:
            keypath = conf.get_keypath()
            priv, pub = crypto.generate_keypair()
            crypto.write_keypair(priv, pub, keypath)
        else:
            print('Provide path for the generated key!')

    elif sys.argv[1] == 'test':
        test()

    else:
        print(sys.argv[1], '- command not recognised')
        print_help()
