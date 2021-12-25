#!/usr/bin/env python3


'''
Communication packet(message) definition.

The protocol is far too simple to involve protobuf.
At least until a second implementation emerges.
But for now the binary layout is hardcoded in the client.
'''


class Packet:
    '''
    Public iface:
        __init__() - create a packet from an encrypted text message
        to_bytes() - create a binary blob from a packet
        from_bytes() - create a packet from a binary blob

    '''
    # System width and endianness don't matter, those constants refer to the protocol.
    INT_WIDTH = 4
    ENDIANNESS = 'little'


    def __init__(me, encrypted: bytes, signature: bytes):
        me.len_encrypted = len(encrypted)
        me.encrypted = encrypted
        me.len_signature = len(signature)
        me.signature = signature


    @classmethod
    def from_bytes(cls, b: bytes):
        '''Alternative ctor.'''
        start = 0
        end = Packet.INT_WIDTH
        len_encrypted = cls._bytes_to_int(b[start:end])

        start = end
        end = end + len_encrypted
        encrypted = b[start:end]

        start = end
        end = end + cls.INT_WIDTH
        len_signature = cls._bytes_to_int(b[start:end])

        start = end
        end = end + len_signature
        signature = b[start:end]
        assert(end == len(b))

        return cls(encrypted, signature)


    def to_bytes(me) -> bytes:
        buff = ( me._int_to_bytes(me.len_encrypted)
               + me.encrypted
               + me._int_to_bytes(me.len_signature)
               + me.signature )
        return buff


    @staticmethod
    def _get_local_endianness():
        import sys
        return sys.byteorder


    @classmethod
    def _int_to_bytes(cls, i: int) -> bytes:
         b = i.to_bytes(cls.INT_WIDTH, byteorder=cls.ENDIANNESS, signed=False)
         return b


    @classmethod
    def _bytes_to_int(cls, b: bytes):
        assert(len(b) == cls.INT_WIDTH)
        i = int.from_bytes(b, byteorder=cls.ENDIANNESS, signed=False)
        return i


    def __eq__(me, other):
        return (me.len_encrypted == other.len_encrypted
            and me.encrypted == other.encrypted
            and me.len_signature == other.len_signature
            and me.signature == other.signature)


def test():
    '''Let`s limit ourselves to ASCII text shorter than 24MB.'''
    msg = b'super!!!!secreT!!*&%#!!.' * int(1e6)
    sign = b'DUMMY_SiGnaTure?!'
    pack = Packet(msg, sign)
    b = pack.to_bytes()
    # Now the binary blob gets transmitted hopefully unchanged.
    newpack = Packet.from_bytes(b)
    assert(newpack == pack)
    print('pack.py: ALL TESTS PASSED')


if __name__ == '__main__':
    test()
