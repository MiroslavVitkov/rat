#!/usr/bin/env python3

'''
This file defines behaviour.
The whole rest of the program marely defines a protocol.
'''


import random
import time


def curse():
    '''
    Random funny curses.
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


def interactive(input_queue):
    '''
    Interactive (classical chat) operation.
    Input is passed via a blocking `multiprocessing.Queue`
        of size 1, for thread safety.
    Output is produced in blocking mode via the yield keyword.
    We are running in our dedicated thread
        but should generally block on input_queue.empty().
    We don't pop() from it as there are probably other readers.
    '''
    while(input_queue.empty()):
        pass  # sleep around
    assert(input_queue.qsize() == 1)
    msg = input_queue.get()
    input_queue.put(msg)  # not allowed to modify it
    #remote = input()
    return curse()


def relay():
    '''A chatroom - broadcasts any message it receives.'''
    pass


def recv_buff():
    '''
    File that records incoming but yet unread messages.
    '''
    pass


def send_buff():
    '''
    File that records sent messages to people that were offline.
    '''
    pass


def log():
    '''A chat history logging utility.'''
    pass


def test():
    for i in range(10):
        assert(len(curse()))
    print('bot.py: ALL TESTS PASSED')


if __name__ == '__main__':
    test()
