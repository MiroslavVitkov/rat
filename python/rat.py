#!/usr/bin/env python3


'''
A peer to peer chat client/server/nameserver entry point.
'''


from threading import Thread
import sys
import socket

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
            print('Dropping', s)
            return

    sock.Server(forever, conf.CHATSERVER)


def relay(ips: [str]=['localhost']) -> None:
    '''
    Host a chatroom. Just proof of concept.
    '''
    peers = set()  # of User objects.

    for ip in ips:
        try:
            say(ip, 'hi bitch')
        except:
            print(ip, 'not listening.')

    # Record the user object once they respond.
    def f(s: socket, a: [bool]=[True]):
        #TODO
        #if s.getpeername() not in ips:
        #    return
        #print('OPTNAME', s.getpeername())

        try:
            client = protocol.handshake_as_server(s)
            peers.add(client)

            priv, _ = crypto.read_keypair()
            while True:
                msg = protocol.recv_msg(s, priv, client.pub, a)
                print(msg.decode('utf8'), len(peers))
                for p in peers:
                    print('PEER', p)
                    say(p.ips[0], '<relay>' + msg.decode('utf8'))
        except:
            return

    sock.Server(f, conf.RELAY_0)


def share( ip: str, text: str) -> None:
    '''
    Send a message to be distributed via a relay.
    '''
    # TODO: specifying port
    own_priv, _ = crypto.read_keypair(conf.get_keypath())

    def func(s: socket):
        remote = protocol.handshake_as_client(s)
        protocol.send_msg(text, s, own_priv, remote.pub)

    sock.Client(func, ip, conf.RELAY_0)


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
    conf.test()
    crypto.test()
    sock.test()
    protocol.test()
    return

    # System test.
    try:
        Thread(target=listen, daemon=True).start()
        Thread(target=say, args=['localhost', 'test', 'message', '!@#'], daemon=True).start()
# TODO: actually send a mesage and validate it was received
        print('\nSYSTEM TEST PASSED')
    except Exception as e:
        print('\nSYSTEM TEST FAILED!')
        print('Reason: ', e)


def print_help() -> None:
    h = '''
        example
        ---
            rat generate
            rat say 46.10.210.37 Unquoted text bro!!!

        chatting
        ---
            rat listen - accept incoming chat messages
            rat say <IP> <message> - unquoted string to send to someone
            rat relay [<IP 1>...<IP n>] - host a relay(chatroom)
            rat share <IP[:port]> <message> - like 'say' but for a relay

        resolving users
        ---
            rat serve - host a nameserver(phonebook)
            rat register <IP 1>...<IP n> - publish details to nameserver(s)
            rat ask <regex> <IP 1>...<IP n> - ask nameservers for user details by regex
            rat vouch <user> <IP 1>...<IP n> - insist this user is who he claims he is
            rat report <user> <IP 1>...<IP n> - indicate a scammer
            rat revoke <IP 1>...<IP n> - delete personal details from nameserver(s)

        video
        ---
            rat stream <IP 1>...<IP n> - export video feed to specified endpoints
            rat watch <IP> -

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

    elif sys.argv[1] == 'share':
        if len(sys.argv) > 3:
            msg = ' '.join(sys.argv[3:])
            share(sys.argv[2], msg)
        else:
            print('Provide a destination IP and a message!')

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

    # TODO: access control?
    elif sys.argv[1] == 'stream':
        protocol.stream_video()

    elif sys.argv[1] == 'watch':
        assert len(sys.argv) == 3
        protocol.watch_video(sys.argv[2])


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
