#!/usr/bin/env python3


'''
A peer to peer chat client.
Refer to the README for dessign goals and usage.
'''


from threading import Thread
import sys
import time

import bot
import conf
import crypto
import name
import pack
from pack import Packet
import prompt
import port
import sock


### Helpers.
def handle_input( s: [sock.socket.socket]
                , own_priv: crypto.Priv
                , remote_pub: [crypto.Pub]
                , alive: bool=True
                ) -> None:
    '''
    We need 2 threads to do simultaneous input and output.
    So let's use the current thread for listening and spin an input one.
    '''
    def inp():
        c = conf.get()['user']
        pr = prompt.get(c['name'], c['group'])
        while alive:
            text = input(pr)
            # Forbid sending empty messages because they DOS the remote peer
            # (the remote network buffer gets clogged).
            # Perhaps a better alternative is to insert a delay in send()?
            # Because what we see on the screen is different from the peer's?
            if text:
                for ip, pub in zip(s, remote_pub):
                    sock.send(text, ip, own_priv, pub)

    Thread(target=inp).start()


def send_user( s: sock.socket.socket
             , own_pub: crypto.Pub ) -> None:
    '''
    Every communication begins with exchanging User objects.
    '''
    u = conf.get()['user']
    user = name.User( u['name']
                    , u['group']
                    , own_pub
                    , sock.get_extern_ip()
                    , u['status'])
    # TODO: encrypt this to prove it's really you that is updating your info.
    s.sendall(user.to_bytes())


### Command handlers.
def serve() -> None:
    '''
    Run a nameserver forever.
    On the standard port.
    Acept all requests from everyone.
    '''
    s = name.Server()


def register(ip, own_pub) -> None:
    def func(s: sock.socket.socket):
        send_user(s, own_pub)
    c = sock.Client(ip=ip, port=port.NAMESERVER, func=func)


def ask(regex, ip) -> None:
    '''Request a list of matching userames from a nameserver.'''
    def func(s: sock.socket.socket):
        s.sendall(regex.encode('utf-8', regex))
        data = sock.recv_one(s)
        try:
            print(name.User.from_bytes(data))
        except:
            # The server reported an error.
            print(data)

    c = sock.Client(ip[0], port=port.NAMESERVER, func=func)


def listen(relay: bool=False) -> None:
        own_priv, own_pub = crypto.generate_keypair()
        remote_sockets = []
        remote_keys = []
        inout = bot.InOut()
        bots = bot.spawn_bots(inout)

        def forever(s):
            # Handshake.
            data = sock.recv_one(s)
            remote_user = name.User.from_bytes(data)
            remote_sockets.append(s)
            remote_keys.append(remote_user.pub)
            send_user(s, own_pub)

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
                print(prompt.get( remote_user.name
                                , remote_user.group)
                     + text)

                # Relay operation.
                if(relay):
                    for socket, key in zip(remote_sockets, remote_keys):
                        if socket != s:
                            sock.send(text, socket, own_priv, key)

        handle_input(remote_sockets, own_priv, remote_keys)
        server = sock.Server(port.CHATSERVER, forever)


def connect( ip: str
           , alive: bool=True
           ) -> None:
    own_priv, own_pub = crypto.read_keypair(conf.get()['user']['keypath'])

    def func(s: sock.socket.socket):
        # Exchange name.User() objects(basically public keys).
        send_user(s, own_pub)
        data = sock.recv_one(s)
        remote_user = name.User.from_bytes(data)
        print('The server identifies as', remote_user)

        # Send messages to the remote peer.
        handle_input((s,), own_priv, (remote_user.pub,))

        # Receive messages from the remote peer.
        for data in sock.recv(s):
            packet = Packet.from_bytes(data)
            text = crypto.decrypt(packet.encrypted, own_priv)
            crypto.verify(text, packet.signature, remote_user.pub)
            print(text)

    client = sock.Client(ip, port.CHATSERVER, func)


def send( ip: str, text: str) -> None:
    own_priv, own_pub = crypto.read_keypair(conf.get()['user']['keypath'])

    def func(s: sock.socket.socket):
        # Exchange public keys.
        send_user(s, own_pub)
        data = sock.recv_one(s)
        remote = name.User.from_bytes(data)

        # Transmit the message and die.
        sock.send(text, s, own_priv, remote.pub)

    client = sock.Client(ip, port.CHATSERVER, func)


def get() -> None:
    pass


def test() -> None:
    sock.test()
    crypto.test()
    pack.test()
    time.sleep(2)
    print('UNIT TESTS PASSED')
    print()

    Thread(target=listen).start()
    time.sleep(1)
    priv, pub = crypto.generate_keypair()
    Thread(target=connect, args=['localhost']).start()
    time.sleep(2)
    print('INTEGRATION TEST PASSED')
    print()
    sys.exit()


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
            rat generate [<path>] - create a new RSA keypair and write it to disk
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
            _, own_pub = crypto.read_keypair(conf.get()['user']['keypath'])
            register(sys.argv[2], own_pub)  # TODO: allow multiple server IPs
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
        if len(sys.argv) == 3:
            keypath = sys.argv[2]
            priv, pub = crypto.generate_keypair()
            crypto.write_keypair(priv, pub, keypath)
        else:
            print('Provide path for the generated key!')

    elif sys.argv[1] == 'test':
        test()

    else:
        print(sys.argv[1], '- command not recognised')
        print_help()
