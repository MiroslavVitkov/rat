#!/usr/bin/env python3


'''
Asymmetric criptography transport layer - basically a dumbified ssl.
'''


import os
from pathlib import Path
import random
import rsa
import tempfile

import conf


Priv = rsa.key.PrivateKey
Pub = rsa.key.PublicKey
Keypair = (Priv, Pub)


HASH = 'SHA-256'
BITS = 1024  # key size
CHUNK_BYTES = SIGNATURE_BYTES = BITS // 8  # 128
MAX_PLAINTEXT_BYTES = CHUNK_BYTES - 11  # 117


# --- Public API.
def from_string(msg: str, own_priv: Priv, remote_pub: Pub) -> bytes:
    return encode_sign_chop_encrypt_stitch(msg, own_priv, remote_pub)


def to_string(msg: bytes, own_priv: Priv, remote_pub: Pub) -> str:
    '''
    Decrypt a string someone sent specifically to us.
    '''
    return chop_decrypt_stitch_verify_decode(msg, own_priv, remote_pub)


def from_bin(msg: bytes, own_priv: Priv, remote_pub: Pub) -> bytes:
    return sign_chop_encrypt_stitch(msg, own_priv, remote_pub)


def to_bin(msg: bytes, own_priv: Priv, remote_pub: Pub) -> bytes:
    return chop_decrypt_stitch_verify(msg, own_priv, remote_pub)


# --- Details.
def encode_sign_chop_encrypt_stitch(msg: str, own_priv: Priv, remote_pub: Pub) -> bytes:
    return sign_chop_encrypt_stitch(msg.encode('utf8'), own_priv, remote_pub)


def sign_chop_encrypt_stitch(msg: bytes, own_priv: Priv, remote_pub: Pub) -> bytes:
    '''
    Example input: 200 byte payload
    Output: [ 128 byte blob over first 117 bytes
            , 128 byte blob over remaining 83 bytes
            , 128 signature over the whole thing]
    '''
    s = sign(msg, own_priv)
    c = chop(msg, MAX_PLAINTEXT_BYTES)
    e = [encrypt(_, remote_pub) for _ in c]
    return stitch(e) + s


def chop_decrypt_stitch_verify_decode(b: bytes, own_priv: Priv, remote_pub: Pub) -> str:
    return chop_decrypt_stitch_verify(b, own_priv, remote_pub).decode('utf8')


def chop_decrypt_stitch_verify(b: bytes, own_priv: Priv, remote_pub: Pub) -> bytes:
    '''
    Last packet is signature, right?
    '''
    d = [decrypt(_, own_priv) for _ in chop(b, CHUNK_BYTES)[:-1]]
    msg = stitch(d)
    verify(msg, chop(b, CHUNK_BYTES)[-1], remote_pub)
    return msg


def generate_keypair(bits: int=BITS) -> Keypair:
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


def chop( b: bytes, max: int=MAX_PLAINTEXT_BYTES ) -> [bytes]:
    '''Split into pieces no longer than max bytes.'''
    return [b[i:i+max] for i in range(0, len(b), max)]


def stitch( bb: [bytes] ) -> bytes:
    '''Collect all packets from one transmission.'''
    ret = bytes()
    [ret := ret + b for b in bb]  # walrus operator updates ret for each b
    return ret


def encrypt(payload: bytes, pub: Pub) -> bytes:
    '''
    Encrypt a message so that only the owner of the private key can read it.
    '''
    assert type(payload) == type(b''), type(payload)
    assert len(payload) <= MAX_PLAINTEXT_BYTES, (len(payload), MAX_PLAINTEXT_BYTES)
    return rsa.encrypt(payload, pub)


def decrypt(encrypted: bytes, priv: Priv) -> bytes:
    '''
    Read a message if it was intended for us.
    '''
    try:
        return rsa.decrypt(encrypted, priv)
    except rsa.pkcs1.DecryptionError:
        # Printing a stack trace leaks information about the key.
        # However prining a trace from here is safe.
        raise rsa.pkcs1.DecryptionError


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
    Only the recepient can validate the sender instead of anyone intercepting.
    '''
    # Convert 'str' to 'bytes'.
    payload = msg
    if type(msg) == str:
        payload = msg.encode('utf8')

    assert type(priv) == Priv, type(priv)
    signature = rsa.sign(payload, priv, HASH)
    return signature


def verify(msg: bytes, signature: bytes, pub: Pub) -> None:
    '''VerificationError - when the signature doesn't match the message.'''
    assert(pub)
    rsa.verify(msg, signature, pub)


def test_chop_stitch():
    # Long payload.
    max = 42
    data = b'This is an extremely long text!' * 666
    packets = chop(data, max)
    assert stitch(packets) == data

    # Binary payload.
    from name import User
    data = User().to_bytes()
    packets = chop(data, max)
    assert stitch(packets) == data


def test_key() -> None:
    priv, pub = generate_keypair()
    p = tempfile.TemporaryDirectory().name
    write_keypair(priv, pub, p)
    newpriv, newpub = read_keypair(p, True)
    assert priv == newpriv, (priv, newpriv)
    assert pub == newpub, (pub, newpub)


def test_encrypt_decrypt():
    # Short strings cover the happy path.
    priv, pub = generate_keypair()
    msg = b'The basic unit of transfer is of course the byte blob - see constants at top.'
    e = encrypt(msg, pub)
    d = decrypt(e, priv)
    assert d == msg

    # Long strings.
    # Chop - encrypt - stitch.
    msg *= 666
    msg_chopped = chop(msg, MAX_PLAINTEXT_BYTES)
    msg_encrypted = [encrypt(msg, priv) for msg in msg_chopped]
    msg_stitched = stitch(msg_encrypted)

    # And vice versa.
    msg_encrypted_2 = chop(msg_stitched, CHUNK_BYTES)
    msg_chopped_2 = [decrypt(m, priv) for m in msg_encrypted_2]
    msg2 = stitch(msg_chopped_2)
    assert msg == msg2

    # Binary payload.
    from name import User
    msg = User().to_bytes()
    e = [encrypt(m, pub) for m in chop(msg, MAX_PLAINTEXT_BYTES)]
    d = stitch([decrypt(en, priv) for en in e])
    assert User.from_bytes(d) == User()


def test_API() -> None:
    priv, pub = generate_keypair()
    msg = 'Random long string.' * 999
    blob = from_string(msg, priv, pub)  # Send to ourselves.
    assert type(blob) == bytes, type(blob)
    msg2 = to_string(blob, priv, pub) # We are the intended recepient so we can read it.
    assert msg == msg2


def test_failures() -> None:
    priv1, pub1 = generate_keypair()
    priv2, pub2 = generate_keypair()

    msg = 'Random long string.' * 99
    blob = from_string(msg, priv1, pub2)  # Send to some random dude.
    # But try to read it ourselves instead.
    try:
        to_string(blob, priv1, pub1)
        raise Exception('test_failures() decrypted nonsence.')
    except rsa.pkcs1.DecryptionError:
        pass

    # He tries to read the message.
    # But enjoys only messages from himself.
    try:
        to_string(blob, priv2, pub2)
        raise Exception('test_failures() ignored a tampered signature.')
    except rsa.VerificationError:
        pass


def test() -> None:
    test_chop_stitch()
    test_key()
    test_encrypt_decrypt()
    test_API()
    test_failures()
    print('crypto.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
