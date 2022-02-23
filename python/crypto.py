#!/usr/bin/env python3


'''
Asymmetric criptography of chat messages.
'''
#TODO: implement perfect foreward secrecy
#Because of forward secrecy an attacker would need to have access to the internal SSH state of either the client or server at the time the SSH connection still exists.
#TODO: protect aainst traffic analysis
# Everything is peer to peer, which is cool, but the IP fetching needs to be anonymysed as well.

import os
from pathlib import Path
import random
import rsa

import conf


Priv = rsa.key.PrivateKey
Pub = rsa.key.PublicKey
Keypair = (Priv, Pub)


# 'MD5', 'SHA-1', 'SHA-224', 'SHA-256', 'SHA-384' or 'SHA-512'
HASH = 'SHA-256'


def generate_keypair(bits: int=1024) -> Keypair:
    pub, priv = rsa.newkeys(bits)
    return priv, pub


def write_keypair( priv: rsa.key.PrivateKey
                 , pub: rsa.key.PublicKey=None
                 , p: Path=conf.get_keypath()
                 ) -> None:
    '''Obviously this function violates the RAM-only constraint.'''
    p = Path(p)
    if p.exists():
        raise BaseException('Refusing to ovewrite an existing private key: '
                           + str(p))
    with open(p, 'wb') as f:
        f.write(priv.save_pkcs1())
    if pub:
        with open(p.with_suffix('.pub'), 'wb') as f:
            f.write(pub.save_pkcs1())


def regenerate_pub(path_priv: Path=conf.get_keypath()) -> None:
    os.system('ssh-keygen -y -f ' + path_priv
             + ' > ' + path_priv + '.pub')


def read_keypair( p: Path=conf.get_keypath()
                , force: bool=False
                , cache: [Keypair]=[]
                ) -> Keypair:
    if cache and not force:
        return cache[0]

    p = Path(p)
    if not p.is_file():
        # This function gets called during static initialization
        # of other modules.
        return None, None

    with open(p, mode='rb') as priv_file:
        key_data = priv_file.read()
        assert key_data
        priv = rsa.PrivateKey.load_pkcs1(key_data)

    pub = None
    if not Path(p.with_suffix('.pub')).is_file():
        regenerate_pub()
    with open(p.with_suffix('.pub'), 'rb') as f:
        key_data = f.read()
        pub = rsa.PublicKey.load_pkcs1(key_data)
    assert pub is not None

    kp = (priv, pub)
    if cache:
        cache[0] = kp
    else:
        cache.append(kp)
    return kp


def encrypt(text: str, pub: Pub) -> bytes:
    '''Encrypt a message so that only the owner of the private key can read it.'''
    bytes = text.encode('utf8')
    encrypted = rsa.encrypt(bytes, pub)
    return encrypted


def decrypt(encrypted: bytes, priv: Priv) -> str:
    try:
        bytes = rsa.decrypt(encrypted, priv)
        string = bytes.decode('utf8')
    except rsa.pkcs1.DecryptionError:
        # Printing a stack trace leaks information about the key.
        print('ERROR: DecryptionError!')
        string = ''
    return string


def sign(msg: str, priv: Priv) -> bytes:
    '''
    Prove you wrote the message.

    It is debatable should signing be performed on the plaintext
    or on the encrypted bytes.

    The former has been chosen because it is not vulnerable to the following.
    Alice sends an encrypted and then signed packet to a server containing a password.
    Eve intercepts the packet, strips the signature, signs it with her own key
    and gets access on the server ever though she doesn't know Alice's password.

    Furthermore it increases privacy.
    Only the recepient can validatet the sender instead of anyone intercepting.
    '''
    signature = rsa.sign(msg.encode('utf8'), priv, HASH)
    return signature


def verify(msg: str, signature: bytes, pub: Pub):
    '''VerificationError - when the signature doesn't match the message.'''
    assert(pub)
    rsa.verify(msg.encode('utf8'), signature, pub)


def test() -> None:
    priv, pub = generate_keypair()
    p = Path('/tmp/whatever' + str(random.randint(0, 1e6)))
    write_keypair(priv, pub, p)
    newpriv, newpub = read_keypair(p, True)
    assert priv == newpriv, (priv, newpriv)
    assert pub == newpub, (pub, newpub)

    msg = "We come in peace!"
    bytes = encrypt(msg, pub)
    newmsg = decrypt(bytes, priv)
    assert msg == newmsg

    signature = sign(msg, priv)
    verify(msg, signature, pub)

    print('crypto.py: ALL TESTS PASSED')


if __name__ == '__main__':
    test()
