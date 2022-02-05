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
def handshake(s: sock.socket.socket, own_pub: crypto.Pub) -> crypto.Pub:
    '''Exchange public keys in cleartext!'''
    data = sock.recv_one()
    remote_pub = crypto.Pub.load_pkcs1(data)
    s.sendall(own_pub.save_pkcs1())
    return remote_pub


def send_( text: str
        , s: sock.socket.socket
        , own_priv: crypto.Priv
        , remote_pub: crypto.Pub
        ) -> None:
    signature = crypto.sign(text, own_priv)
    encrypted = crypto.encrypt(text, remote_pub)
    msg = Packet(encrypted, signature).to_bytes()
    s.sendall(msg)


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
            for ip, pub in zip(s, remote_pub):
                send_(text, ip, own_priv, pub)

    Thread(target=inp).start()


def send_user( s: sock.socket.socket
             , own_pub: crypto.Pub ):
    '''
    Every communication begins with exchanging User objects.
    '''
    u = conf.get()['user']
    ip = sock.Server(0, '').ip
    user = name.User( u['name']
                    , own_pub
                    , ip
                    , u['status'])
    # TODO: encrypt this to prove it's really you that is updating your info.
    s.sendall(user.to_bytes())


### Command handlers.
def serve():
    '''
    Run a nameserver forever.
    On the standard port.
    Acept all requests from everyone.
    '''
    s = name.Server()


def register(ip, own_pub):
    def func(s: sock.socket.socket):
        serv = sock.Server(0, lambda: 0)
        serv.alive = False
        ip = serv.ip
        u = name.User( conf.get()['user']['name']
                     , own_pub
                     , ip
                     , conf.get()['user']['status'])
        s.sendall(u.to_bytes())
    c = sock.Client(ip=ip, port=port.NAMESERVER, func=func)


def ask(regex, ip, timeout=5):
    '''Request a list of matching userames from a nameserver.'''
    def func(s: sock.socket.socket):
        s.sendall(regex.encode('utf-8', regex))
        s.settimeout(timeout)
        while True:
            try:
                data = s.recv(4296)  # TODO
                print(name.User.from_bytes(data))
                return
            except:
                # Probably timed out.
                return
    c = sock.Client(ip[0], port=port.NAMESERVER, func=func)


def listen():
        own_priv, own_pub = crypto.generate_keypair()
        remote_sockets = []
        remote_keys = []

        def forever(s):
            # Handshake.
            data = sock.recv_one():
            remote_user = name.User.from_bytes(data)
            remote_sockets.append(s)
            remote_keys.append(remote_user.pub)
            ip = sock.Server(0, '').ip
            us = name.User('a chat server', own_pub, ip, 'wellcome')  # TODO: read conf
            s.sendall(us.to_bytes())
            break

            # Accept text messages.
            for data in sock.recv():
                assert len(data) < MAX_MSG_BYTES, (len(data), MAX_MSG_BYTES)
                packet = Packet.from_bytes(data)
                text = crypto.decrypt(packet.encrypted, own_priv)
                crypto.verify(text, packet.signature, remote_user.pub)
                print(text)

        handle_input(remote_sockets, own_priv, remote_keys)
        server = sock.Server(port.CHATSERVER, forever)


def connect( ip: str
           , own_priv: crypto.Priv
           , own_pub: crypto.Pub
           , alive: bool=True
           ):
    def func(s: sock.socket.socket):
        # Exchange public keys.
        send_user(s, own_pub)
        while alive:
            data = s.recv(MAX_MSG_BYTES)
            if data:
                remote_user = name.User.from_bytes(data)
                print('The server identifies as', remote_user)
                break

        # Send messages to the remote peer.
        handle_input((s,), own_priv, (remote_user.pub,))

        # Receive messages from the remote peer.
        while alive:
            data = s.recv(MAX_MSG_BYTES)
            if data:
                packet = Packet.from_bytes(data)
                text = crypto.decrypt(packet.encrypted, own_priv)
                crypto.verify(text, packet.signature, remote_user.pub)
                print(text)
            time.sleep(0.1)


        # TEST: spawn an interactive bot that only listens
        return
        inout = bot.InOut()
        t = Thread(target=bot.interactive, args=[inout]).start()
        while alive:
            data = s.recv(MAX_MSG_BYTES)
            packet = Packet.from_bytes(data)
            text = crypto.decrypt(packet.encrypted, own_priv)
            crypto.verify(text, packet.signature, remote_user.pub)
            inout.in_msg = text
            with inout.in_cond:
                inout.in_cond.notify_all()
        return

        while False:
             insult = bot.curse()
             send_(insult, s, own_priv, remote_pub)
             time.sleep(bot.random.randint(1,8))

    client = sock.Client(ip, port.CHATSERVER, func)


def send():
    pass


def get():
    pass


def test():
    sock.test()
    crypto.test()
    pack.test()
    time.sleep(2)
    print('UNIT TESTS PASSED')
    print()

    Thread(target=listen).start()
    time.sleep(1)
    priv, pub = crypto.generate_keypair()
    Thread(target=connect, args=['localhost', priv, pub]).start()
    time.sleep(2)
    print('INTEGRATION TEST PASSED')
    print()
    sys.exit()


def print_help():
    h = '''
        Usage:

        resolving users
        ---
            rat serve - start a nameserver
            rat register <ip> - publish details to a nameserver
            rat ask <regex> <ip>  - ask a nameservers for user details

        chatting
        ---
            rat listen - accept incoming chats, interactively
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

    elif sys.argv[1] == 'connect':
        if len(sys.argv) == 3:
            priv, pub = crypto.read_keypair(conf.get()['user']['keypath'])
            connect(sys.argv[2], priv, pub)
        else:
            print('Provide the IP to connect to, it must be listening!')

    elif sys.argv[1] == 'send':
        if len(sys.argv) >= 3:
            pass  # send argv2 some message
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
