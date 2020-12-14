#!/usr/bin/env python3

'''
A demo of how to script the client.
'''


import rat

import random


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


if __name__ == '__main__':
    pass
