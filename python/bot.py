#!/usr/bin/env python3

'''
This file defines behaviour.
The whole rest of the program marely defines a protocol.

Each bot runs in a separate thread spawned in rat.py
because it could produce output(==send to remote peer) at any time.

This module deals only with strings; they are passed/received via rat.py.

Overview of python synchronization primitives.
- from queue import Queue as Q; q = Q(maxsize=1); q.put(); q.get(); q.qempty()
    Is thread safe but can't peek().
    Yet all bots expect to see the same message without pop()-ing.
    Furthermore polling qempty() takes up a whole CPU core.
- from threading import Lock as L; l = L(); l.acquire(); l.release()
    A semaphore of seize 1.
    Implemented in low level module _thread.
- from threading import Condition as C; c = C(); c.wait(); c.notify_all()
    wait() releases the lock and waits for a notify() to get it back.
    Difference from Lock is both notify() and releasing the lock are needed.
- from threading import Event as E; e = E(); e.set(); e.clear(); e.wait()
    Event gets fired continously.
'''


import random
#from queue import Queue
from threading import Condition, Thread
import time

from name import User


### Helpers.
class InOut:
    '''
    Thread synchronised input and output to bots(from rat.py).
    '''
    def __init__(me):
        # Input from zero or one users.
        me.sender = User(None, None, None)
        me.in_cond = Condition()
        me.in_msg = ''

        # Output to zero or several users.
        # Let's figure out the input and then we'll refine this mapping here.
        me.recepients = [User(None, None, None)]
        me.out_cond = Condition()
        me.out_msg = ['']


def spawn_bots(inout: InOut) -> [Thread]:
    '''
    Invoke all bots requested in conf.ini.
    '''
    bot_threads = []
    for b in conf.get()['user']['bots'].split(','):
        b = b.strip()  # remove whitespaces
        bot_func = getattr(bot, b)
        t = Thread(target=bot_func, args=[inout]).start()
        bot_threads.append(t)
    return bot_threads


### Actual bots.
def curse():
    '''
    Random funny curses.

    in - none
    out - return
    '''
    adj = ( 'abnormal', 'brainwashed', 'insufferable', 'propostorous'
          , 'silly', 'smelly', 'stupid')
    noun = ('miscreant', 'blackguard', 'criminal', 'lawbreaker', 'outlaw',
            'offender', 'felon', 'convict', 'jailbird', 'malefactor',
            'wrongdoer', 'black hat', 'supervillain', 'transgressor',  'sinner',
            'gangster', 'gunman', 'bandit', 'brigand', 'desperado', 'thief',
            'robber', 'mugger', 'swindler', 'fraudster', 'racketeer', 'zombie,'
            'terrorist', 'pirate', 'rogue', 'scoundrel', 'wretch heel',
            'reprobate', 'charlatan', 'evil-doer', 'ruffian', 'hoodlum',
            'hooligan', 'thug', 'delinquent', 'never-do-well', 'good-for-nothing',
            'malfeasant', 'misfeasor', 'infractor', 'knave', 'rake', 'crook',
            'con baddie', 'shark', 'rat', 'snake', 'snake in the grass',
            'dog', 'hound', 'louse', 'swine', 'scumbag', 'cretin', 'fool',
            'wrong and crim rotter', 'bounder', 'bad egg', 'stinker')

    insult = ( 'You '
             + random.choice(adj) + ' '
             + random.choice(adj) + ' '
             + random.choice(adj) + ' '
             + random.choice(noun)
             + '!'
             )

    return insult


def handle_input( s#: [sock.socket.socket]
                , own_priv#: crypto.Priv
                , remote_pub#: [crypto.Pub]
                , alive: bool=True
                ) -> None:
    '''
    Not a bot!
    We need 2 threads to do simultaneous input and output.
    So let's use the current thread for listening and spin an input one.
    '''
    def inp():
        c = get_conf()['user']
        pr = prompt.get(c['name'], c['group'])
        while alive:
            text = input(pr)
            for ip, pub in zip(s, remote_pub):
                send(text, ip, own_priv, pub)

    return Thread(target=inp).start()


def interactive(inout: InOut):
    '''
    Interactive (classical chat) operation.
    We are running in our dedicated thread.
    '''
    # Print the input we have just received.
    with inout.in_cond:
        inout.in_cond.wait()
        print(inout.in_msg)

    # Generate output message, todo.
    prompt = '->'
    #out_thread = handle_input()
    return curse()


def non_interactive():
    '''
    Example operation:
    rat send <username> <some text>
    rat get

    Recommended to be used witha send and especially recv buffers.

    in - param
    out - return
    '''


def relay():
    '''
    A chatroom - broadcasts any message it receives.

    in - async(in Q)
    out - async(out Q)  !!!! how do we send to everyone?!?!
    '''
    pass


def recv_buff():
    '''
    File that records incoming but yet unread messages.

    in - param
    out - ?!??!?!?
    '''
    pass


def recv_rambuff():
    '''
    '''
    pass


def send_buff():
    '''
    File that records sent messages to people that were offline.
    '''
    pass


def log():
    '''
    A chat history logging utility.

    in - param
    out - none (just appends a file)
    '''
    pass


def test():
    # Test curse() bot.
    for i in range(10):
        assert(len(curse()))

    # Test InOut class.
    inout = InOut()
    def foo():
        with inout.in_cond:
            inout.in_cond.wait()
            print(inout.in_msg)
    t = Thread(target=foo)
    t.start()
    inout.in_msg = 'Some input message from the remote peer.'
    with inout.in_cond:
        inout.in_cond.notify_all()
    t.join()

    # We're done.
    print('bot.py: ALL UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
