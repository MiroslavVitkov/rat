#!/usr/bin/env python3


'''
A peer to peer chat client/server/nameserver entry point.
'''


from threading import Thread
import sys
import socket

from impl import conf
from impl import crypto
from impl import sock

from prot import chat
from prot import handshake
from prot import name
from prot import video


def say( ip: str, text: str) -> None:
    '''
    Send a text message to someone listening and disconnect.
    Example: $rat say localhost hey bryh, wazzup
    '''
    own_priv, _ = crypto.read_keypair(conf.get()['crypto']['keypath'])

    def func(s: socket):
        '''Transmit a message and die.'''
        remote = handshake.as_client(s)
        chat.send_msg(text, s, own_priv, remote.pub)

    sock.Client(func, ip, conf.CHATSERVER)


def listen() -> None:
    '''
    Accept and display incoming messages.
    '''
    def forever(s: socket, a: [bool]):
        try:
            # Handshake.
            client = handshake.as_server(s)
            print('The remote user identifies as', client)

            # Accept messages.
            priv, _ = crypto.read_keypair()
            while True:
                msg = chat.recv_msg(s, priv, client.pub, a)
                # warn: without 'flush' systemd does not log this!
                print(msg.decode('utf8'), flush=True)
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
            client = handshake.as_server(s)
            peers.add(client)

            priv, _ = crypto.read_keypair()
            while True:
                msg = chat.recv_msg(s, priv, client.pub, a)
                print(msg.decode('utf8'), len(peers))
                for p in peers:
                    say(p.ips[0], '<relay>' + msg.decode('utf8'))
        except:
            return

    sock.Server(f, conf.RELAY_0)


def share( ip: str, text: str) -> None:
    '''
    Send a message to be distributed via a relay.
    '''
    # TODO: specifying port
    own_priv, _ = crypto.read_keypair(conf.get()['crypto']['keypath'])

    def func(s: socket):
        remote = handshake.as_client(s)
        chat.send_msg(text, s, own_priv, remote.pub)

    sock.Client(func, ip, conf.RELAY_0)


def connect(ip:str) -> None:
    pass


def ask(regex: str, ip: [str]) -> None:
    '''Request a list of matching userames from a nameserver.'''
    own_priv, _ = crypto.read_keypair()
    def f(s: socket):
        server = handshake.as_client(s)
        chat.send_msg(regex, s, own_priv, server.pub)
        data = chat.recv_msg(s, own_priv, server.pub)
        user = name.User.from_bytes(data)
        print(user)

    c = sock.Client(func=f, ip=ip[0], port=conf.NAMESERVER)


def register(ip: [str]) -> None:
    '''
    Register our User object(conf.ini + pub key) with nameserver(s).
    '''
    def func(s: socket):
        server = handshake.as_client(s)
        own_priv, _ = crypto.read_keypair()
        chat.send_msg(b'register', s, own_priv, server.pub)

    sock.Client(ip=ip[0], port=conf.NAMESERVER, func=func)


def watch( remote: str ) -> None:
    '''Spawn a video player and stream in from remote.'''
    video.watch(remote)


def stream() -> None:
    '''Stream camera to conf.VIDEO.'''
    s = video.stream()


def serve() -> None:
    '''
    Run a nameserver forever.
    On the standard port.
    Acept all requests from everyone.
    '''
    name.Server()


def get_prompt( name: str=conf.get()['about']['name']
              , group:str=conf.get()['about']['group']
              ) -> str:
    return (name + '@' + group + '<-')


def test() -> None:
    # An `os.listdir('.')` wouldn't allow us to selectively disable tests.
    conf.test()
    crypto.test()
    sock.test()
    video.test()

    chat.test()
    handshake.test()
    name.test()

    return 0  # warn: see a93a57d

    # System test.
    try:
        Thread(target=listen, daemon=True).start()
        # Warn: running a separate thread fails to cathch exceptions.
        say('localhost', 'Test message!@#')
        print('\nSYSTEM TEST PASSED')
        return 0
    except Exception as e:
        print('\nSYSTEM TEST FAILED!')
        print('Reason: ', e)
        return -1


def print_help() -> None:
    h = '''
        example
        ---
            rat generate
            rat say rat.pm Unquoted text bro!!!

        chatting
        ---
            rat listen - accept incoming chat messages
            rat say <IP> <message> - unquoted string to send to someone
            rat relay [<IP 1>...<IP n>] - host a relay(chatroom)
            rat share <IP[:port]> <message> - like 'say' but for a relay
            rat connect <IP> - like 'say' but works behind a firewall

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
        stream()

    elif sys.argv[1] == 'watch':
        assert len(sys.argv) == 3
        watch(sys.argv[2])

    elif sys.argv[1] == 'generate':
        assert len(sys.argv) == 2
        priv, pub = crypto.generate_keypair()
        crypto.write_keypair(priv, pub)

    elif sys.argv[1] == 'test':
        sys.exit( test() )

    else:
        print(sys.argv[1], '- command not recognised')
        print_help()
