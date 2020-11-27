#!/usr/bin/env python3


'''
Asymmetric criptography of chat messages.
'''


import os
from pathlib import Path
import rsa


# Location to first look for a private key.
DEFAULT_PRIV = Path(Path.home() / '.ssh/id_rsa')


def generate_keypair(bits: int=1024) -> (rsa.key.PrivateKey, rsa.key.PublicKey):
    pub, priv = rsa.newkeys(bits)
    return priv, pub


def write_keypair(priv: rsa.key.PrivateKey
                 , pub: rsa.key.PublicKey=None
                 , p: Path=DEFAULT_PRIV):
    '''Obviously this function violates the RAM-only constraint.'''
    if p.exists():
        raise BaseException('Refusing to ovewrite an existing private key.')
    with open(p, 'wb') as f:
        f.write(priv.save_pkcs1())
    if pub:
        with open(p.with_suffix('.pub'), 'wb') as f:
            f.write(pub.save_pkcs1())


def regenerate_pub(path_priv: Path=DEFAULT_PRIV):
    os.run('ssh-keygen -y -f ' + path_priv
          + ' > ' + path_priv + '.pub')


def read_keypair(p: Path=DEFAULT_PRIV):
    with open(p, mode='rb') as priv_file:
        key_data = priv_file.read()
        priv = rsa.PrivateKey.load_pkcs1(key_data)

    pub = None
    if not Path(p.with_suffix('.pub')).is_file():
        regenerate_pub()
    with open(p.with_suffix('.pub'), 'rb') as f:
        key_data = f.read()
        pub = rsa.PublicKey.load_pkcs1(key_data)
    assert(pub is not None)

    return priv, pub


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
    rsa.verify(bytes, signature, pub)


def test():
    priv, pub = generate_keypair()
    write_keypair(priv, pub, Path('/tmp/whatever'))
    newpriv, newpub = read_keypair(Path('/tmp/whatever'))
    assert(priv == newpriv)
    assert(pub == newpub)

if __name__ == '__main__':
    test()