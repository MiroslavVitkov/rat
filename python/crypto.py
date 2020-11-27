#!/usr/bin/env python3


'''
Asymmetric criptography of chat messages.
'''


import rsa


def create_keypair(bits=1024):
    pub, priv = rsa.newkeys(bits)
    return pub, priv


def write_keypair(path='~/.ssh/id_rsa'):
    '''Obviously this function violates the RAM-only constraint.'''
    pass  # TODO


# TODO The private key can be generated from the public one.
def read_keypair(path='~/.ssh/id_rsa'):
    with open(path, mode='rb') as privatefile:
        keydata = privatefile.read()
        priv = rsa.PrivateKey.load_pkcs1(keydata)
        pub = None  # TODO
        return pub, priv


def encrypt(text, pub):
    '''Encrypt a message so that only the owner of the private key can read it.'''
    bytes = text.encode('utf8')
    encrypted = rsa.encrypt(bytes, pub)
    return encrypted


def decrypt(encrypted, priv):
    try:
        bytes = rsa.decrypt(encrypted, priv)
        string = bytes.decode('utf8')
    except rsa.pkcs1.DecryptionError:
        # Printing a stack trace leaks information about the key.
        print('DecryptionError')
    return string


def sign(bytes, priv):
    '''Prove you wrote the message.'''
    signature = rsa.sign(bytes, priv)
    return signature


def verify(bytes, pub):
    '''VerificationError - when the signature doesn't match the message.'''
    rsa.verify(bytes, signature, pub):


def test():
    pass

if __name__ == '__main__':
    test()
