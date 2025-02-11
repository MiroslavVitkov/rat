#!/usr/bin/env python3


'''
Configuration povider, mainly via a config file parser, but ports are hardcoded.
'''


from configparser import ConfigParser
import os
import pickle


# Standard ports used by the program.
CHATSERVER = 42666
NAMESERVER = CHATSERVER + 1
TEST = NAMESERVER + 1


def where_are_we():
    '''
    Return path to the dir containing this file.
    Otherwise relative paths are relative to the working dir
    and that is the dir the script was invoked from.
    '''
    file_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(file_path)
    return dir_path


def get(path: str=where_are_we()+'/../conf.ini', c: list=[]):
    '''
    Use like:
        get_conf()['section_name']['setting_name']
    '''
    if not len(c):
        c_ = ConfigParser()
        c_.read(path)
        c.append(c_)

    return c[0]


def get_keypath():
    p = get()['user']['keypath']
    return os.path.expanduser(p)


class User:
    '''
    A 'user' is defined by their public key.
    Meaning 5 devices with the same key - one logical user.
    rat is supposed to allow different users to perform code paths in a single invocation.
    '''
    U = get()['user']


    def __init__( me
                , name: str=U['name']
                , group: str=U['group']
                , pub=None
                , ips: [str]=[]
#                , pub: crypto.Pub=crypto.read_keypair()[1]
#                , ips: [str]=[sock.get_extern_ip()]
                , status: str=U['status']
                ):
        me.name = name
        me.group = group
        me.pub = pub
        me.ips = ips
        me.status = status


    @classmethod
    def from_bytes(cls, b: bytes) -> 'User':
        obj = pickle.loads(b)
        assert type(obj) == cls, (type(obj), cls)
        return obj


    def to_bytes(me) -> bytes:
        return pickle.dumps(me)


    def __repr__(me) -> str:
        assert(me)
        assert(me.pub)
        pub = str(me.pub.save_pkcs1())
        ips = ', '.join(me.ips)
        return ( '\n'
               + 'nickname: ' + me.name + '\n'
               + 'group: ' + me.group + '\n'
               + 'public key: ' + pub + '\n'
               + 'IPs: ' + ips + '\n'
               + 'status: ' + me.status)

    def __eq__(me, other):
        if type(me) != type(other):
            return False;
        return me.__dict__ == other.__dict__


def test():
    assert User.from_bytes(User().to_bytes()) == User()

    # Ensure fields exist and are non-empty.
    assert len(get()['user']['name'])
    assert len(get()['user']['group'])
    assert len(get()['user']['status'])
    assert len(get()['user']['keypath'])
    # ['user']['bots'] is empty by default.

    print('conf.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
