#!/usr/bin/env python3


'''
A peer to peer chat client.
Refer to the README for dessign goals and usage.
'''


# Thread safe; there's also multiprocessing.Queue for ... processes.
from queue import Queue
from threading import Thread
import time

import bot
import conf
import crypto
import name
import pack
import prompt
import port
import sock


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
        u = name.User( get_conf()['user']['name']
                     , own_pub
                     , ip
                     , get_conf()['user']['status'])
        s.sendall(u.to_bytes())
    c = sock.Client(ip=ip, port=port.NAMESERVER, func=func)


def ask(regex, ip, timeout=5):
    '''Request a list of matching userames from a nameserver.'''
    def func(s: sock.socket.socket):
        s.sendall(regex.encode('utf-8', regex))
        s.settimeout(timeout)
        while True:
            try:
                data = s.recv(1024)
                print(name.User.from_bytes(data))
                return
            except:
                # Probably timed out.
                return
    c = sock.Client(ip[0], port=port.NAMESERVER, func=func)


def handshake(s: sock.socket.socket, own_pub: crypto.Pub) -> crypto.Pub:
    '''Exchange public keys in cleartext!'''
    while True:
        data = s.recv(1024)
        if data:
            remote_pub = crypto.Pub.load_pkcs1(data)
            s.sendall(own_pub.save_pkcs1())
            return remote_pub


def send( text: str
        , s: sock.socket.socket
        , own_priv: crypto.Priv
        , remote_pub: crypto.Pub
        ) -> None:
    signature = crypto.sign(text, own_priv)
    encrypted = crypto.encrypt(text, remote_pub)
    msg = pack.Packet(encrypted, signature).to_bytes()
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
                send(text, ip, own_priv, pub)

    Thread(target=inp).start()


def listen():
        own_priv, own_pub = crypto.generate_keypair()
        remote_sockets = []
        remote_keys = []

        def forever(s):
            # Handshake.
            while True:
                data = s.recv(1024)
                if data:
                    remote_user = name.User.from_bytes(data)
                    remote_sockets.append(s)
                    remote_keys.append(remote_user.pub)
                    ip = sock.Server(0, '').ip
                    us = name.User('a chat server', own_pub, ip, 'wellcome')
                    s.sendall(us.to_bytes())
                    break

            # Accept text messages.
            while True:
                data = s.recv(1024)
                if data:
                    assert(len(data) < 1024)
                    packet = pack.Packet.from_bytes(data)
                    text = crypto.decrypt(packet.encrypted, own_priv)
                    crypto.verify(text, packet.signature, remote_user.pub)
                    print(text)
                time.sleep(0.1)

        handle_input(remote_sockets, own_priv, remote_keys)
        server = sock.Server(port.CHATSERVER, forever)
        time.sleep(10)
        server.alive = False


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


def connect( ip: str
           , own_priv: crypto.Priv
           , own_pub: crypto.Pub
           , alive: bool=True
           ):
    def func(s: sock.socket.socket):
        send_user(s, own_pub)
        # Receive server public key.
        while alive:
            data = s.recv(1024)
            if data:  # ??!
                remote_user = name.User.from_bytes(data)
                print('The server identifies as', remote_user)
                break

        handle_input((s,), own_priv, (remote_user.pub,))

        # TEST: spawn an interactive bot that only listens
        inout = bot.InOut()
        t = Thread(target=bot.interactive, args=[inout]).start()
        while alive:
            data = s.recv(1024)
            packet = pack.Packet.from_bytes(data)
            text = crypto.decrypt(packet.encrypted, own_priv)
            crypto.verify(text, packet.signature, remote_user.pub)
            inout.in_msg = text
            with inout.in_cond:
                inout.in_cond.notify_all()
        return




        # Accept text messages.
        q = Queue(maxsize=1)
        while alive:
            data = s.recv(1024)  # TODO: handle longer packets
            if data:
                packet = pack.Packet.from_bytes(data)
                text = crypto.decrypt(packet.encrypted, own_priv)
                crypto.verify(text, packet.signature, remote_user.pub)
                assert(q.empty())
                q.put(text)
                #print(text)
            time.sleep(0.1)

            # TODO: mirror bot logic into serve()
            bot_threads = bot.spawn_bots(q)
            assert(q.full())
            q.get()  # drop()

        while False:
             insult = bot.curse()
             send(insult, s, own_priv, remote_pub)
             time.sleep(bot.random.randint(1,8))

    client = sock.Client(ip, port.CHATSERVER, func)


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
            rat listen - accept incoming chats
            rat connect <ip> - start chatting if they are listening

        miscellaneous
        ---
            rat generate [<path>] - create a new RSA keypair and write it to disk
            rat test - run all unnit and integration tests
            rat help - print this message
        '''
    print(h)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2 or sys.argv[1] == 'help':
        print_help()

    elif sys.argv[1] == 'generate':
        assert(len(sys.argv) == 3)
        keypath = sys.argv[2]
        priv, pub = crypto.generate_keypair()
        crypto.write_keypair(priv, pub, keypath)

    elif sys.argv[1] == 'serve':
        serve()

    elif sys.argv[1] == 'register':
        _, own_pub = crypto.read_keypair(get_conf()['user']['keypath'])
        register(sys.argv[2], own_pub)

    elif sys.argv[1] == 'ask':
        if len(sys.argv) >= 4:
            ask(sys.argv[2], sys.argv[3:len(sys.argv)])
        else:
            print('To query namserververs please provide your regex and their IPs.')

    elif sys.argv[1] == 'listen':
        listen()
    elif sys.argv[1] == 'connect':
        priv, pub = crypto.read_keypair(get_conf()['user']['keypath'])
        connect(sys.argv[2], priv, pub)
    elif sys.argv[1] == 'test':
        test()
    elif sys.argv[1] == 'send':
        pass  # send argv2 some message
    elif sys.argv[1] == 'get':
        pass  # pop all accumulated messages from the reveice buffer
    else:
        print(sys.argv[1], '- command not recognised')
        print_help()
