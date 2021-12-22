#!/usr/bin/env python3

'''
A demo of how to script the client.
'''


import random
import time


# synonims of villain:
# miscreant blackguard criminal lawbreaker outlaw offender felon convict jailbird malefactor wrongdoer black hat supervillain transgressor sinner gangster gunman bandit brigand desperado thief robber mugger swindler fraudster racketeer terrorist pirate rogue scoundrel wretch heel reprobate charlatan evil-doer ruffian hoodlum hooligan thug delinquent ne'er-do-well good-for-nothing malfeasant misfeasor infractor cad knave rake crook con baddie shark rat snake snake in the grass dog hound louse swine scumbag wrong 'un crim rotter bounder bad egg stinker


def curse():
    adj = ( 'abnormal', 'brainwashed', 'insufferable', 'propostorous'
          , 'silly', 'smelly', 'stupid')
    noun = ('dog', 'cretin', 'evil-doer', 'fool', 'zombie')

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
