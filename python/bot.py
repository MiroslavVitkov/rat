#!/usr/bin/env python3

'''
This file defines behaviour.
The whole rest of the program marely defines a protocol.
'''


import random
import time


def curse():
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
            'con baddie', 'shark', 'rat', 'snake', 'snake in the grass'
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


def relay():
    '''A chatroom.'''
    pass


def log():
    '''A chat history logging utility.'''
    pass


if __name__ == '__main__':
    for i in range(10):
        print(curse())
    print('bot.py: ALL TESTS PASSED')
