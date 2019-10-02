import json
import logging
import textwrap

import prime
from utils import *

logger = logging.getLogger('rsa')

def hex_or_none(x):
    if type(x) in IntTypes:
        return '0x%x' % x
    else:
        return None

class RSAKey(object):
    KEYS = ['N', 'e']

    @staticmethod
    def from_json(json_str):
        def as_int(x):
            if type(x) in IntTypes:
                return x
            elif type(x) is str and x.startswith('0x'):
                return int(x, 16)
            else:
                return int(x, 10)
        d = { k: as_int(v) for k, v in json.loads(json_str).items() }
        return RSAKey(**d)

    def __init__(self, N=None, e=None, d=None, p=None, q=None, dp=None, dq=None, qinv=None, temp_p=None,bits=None,seed=None):
        """
        One of following set of parameters must be given:
            (N, e), (N, d), (dp, dq, qinv), (e, p, q), (bits)
        """
        self.p = self.q = self.phi = self.dp = self.dq = self.e = None

        if p != None and q != None:
            self.p, self.q = p, q
            self.phi = (p - 1) * (q - 1)
            self.N = p * q
        elif N != None:
            self.N = N

        elif bits != None:
            self.e = 0x10001
            self.gen_pq(bits,seed)
   
        else:
            raise ValueError('N or (p, q) or bits must be given')

        if e != None:
            self.e = e

        if d:
            self.d = d

        elif self.phi:
            self.d = modinv(self.e, self.phi)
        
        else:
            self.phi = self.d = None

        if self.phi:
            assert self.e < self.phi

        if dp and dq:
            self.dp = dp
            self.dq = dq

        elif self.p and self.q:
            self.dp = modinv(self.e, self.p - 1)
            self.dq = modinv(self.e, self.q - 1)

        if self.dp and self.dq:
            if qinv:
                self.qinv = qinv
            elif self.p and self.q:
                self.qinv = modinv(self.q, self.p)
            else:
                raise ValueError('dp, dq were given, but can not compute qinv')

        if not self._can_decrypt: # at last, we assume e = 65537
            self.e = 0x10001

    def gen_pq(self, bits, seed):
        """
        generate keypair (p, q)
        """
        l = bits >> 1

        while True:
            p = prime.randprime_bits(seed,l)
            if prime.is_probable_prime(p, None, l // 8):
                break

        while True:
            q = prime.randprime_bits(seed,bits - l)
            if p != q and prime.is_probable_prime(q, None, l // 8):
                break

        self.temp_p = p
        self.temp_q = q
        self.N = p * q

    def gen_private(self, bits):
        l = bits >> 1
        p = 2 ** l
        
        while True:
            if prime.is_probable_prime(p,None, l // 8):
                if self.N % p == 0 :
                    q = self.N // p
                    if prime.is_probable_prime(q,None,l//8):
                        self.p = p
                        self.q = q
                        self.phi = (p-1)*(q-1)
                        self.d = modinv(self.e,self.phi)
                        break
                        
            p = p+1
                        

    @property
    def _can_encrypt(self):
        return self.N and self.e

    @property
    def _can_decrypt(self):
        return self.N and self.d

    @property
    def _can_crt(self):
        return self.N and self.dq and self.dp and self.qinv and self.p and self.q

    @property
    def block_size(self):
        return (self.N.bit_length() + 7) >> 3

    def __repr__(self):
        return 'RSAKey(%s)' % ', '.join('%s=%s' % (k, hex_or_none(getattr(self, k, None))) for k in self.KEYS)

    def as_dict(self):
        """
        dump this key object as dict object
        """
        return { k: hex_or_none(getattr(self, k, None)) for k in self.KEYS }

    def to_json(self):
        """
        dump this key object as JSON
        """
        return json.dumps(self.as_dict())

    def dump(self):
        """
        print fields of this key object to stdout
        """
        def pref_generator(headline):
            yield headline
            prefspc = ' ' * len(headline)
            while True:
                yield prefspc

        def dump_attr(attrname, ident=4):
            val = getattr(self, attrname, None)
            if not val:
                print(' ' * ident + '%4s = None' % attrname)
            else:
                headline = ' ' * ident + '%4s = ' % attrname
                print('\n'.join(p + i for p, i in zip(pref_generator(headline), textwrap.wrap('0x%x,' % val))))
        print('RSAKey {')
        for attr in self.KEYS:
            dump_attr(attr)
        print('}')

    def simplify(self):
        """
        return simplified RSAKey object (only {N, e, d} fields)
        """
        return RSAKey(N=self.N, e=self.e, d=self.d)


class RSA(object):
    def __init__(self, bits=None, seed = None):
            self.key = RSAKey(bits=bits, seed = seed)
            self.bits = bits
            self.seed = seed

    def encrypt(self, msg):
        """
        msg     little-endian ordered bytes or int
        """
        if not self.key._can_encrypt:
            raise AttributeError('This key object can not do encryption')
        if type(msg) not in IntTypes:
            msg = bytes2int(ensure_bytes(msg))

        return pow(msg, self.key.e, self.key.N)

    def decrypt(self, msg, useCRT=False):
        """
        msg     little-endian ordered bytes or int
        """
        #self.key.gen_private(self.bits)

        if not self.key._can_decrypt:
            raise AttributeError('This key object can not do decryption')
        if type(msg) not in IntTypes:
            msg = bytes2int(ensure_bytes(msg))

        if self.key._can_crt:
            return self._crt_decrypt(msg)
        elif useCRT:
            raise Exception('CRT optimize not available for this key object')
        else:
            return pow(msg, self.key.d, self.key.N)

    def _crt_decrypt(self, msg):
        m1 = pow(msg % self.key.p, self.key.dp, self.key.p)
        m2 = pow(msg % self.key.q, self.key.dq, self.key.q)
        k = (self.key.qinv * (m1 - m2 + self.key.p)) % self.key.p
        return m2 + k * self.key.q

    def encrypt_block(self, msg):
        return int2bytes(self.encrypt(msg), self.key.block_size)

    def decrypt_block(self, msg, useCRT=False):
        return int2bytes(self.decrypt(msg), self.key.block_size - 1)

    def encrypt_data(self, data):
        bs = self.key.block_size - 1
        data_stream = (data[i:i+bs] for i in range(0, len(data), bs))
        return b''.join(self.encrypt_block(block) for block in data_stream)

    def decrypt_data(self, data):
        useCRT = self.key._can_crt
        if useCRT:
            logger.info('CRT optimize are used')

        bs = self.key.block_size
        data_stream = (data[i:i+bs] for i in range(0, len(data), bs))
        return b''.join(self.decrypt_block(block, useCRT)[:bs-1] for block in data_stream).rstrip(b'\x00')

def random_str(l):
    import os
    return Bytes(bytearray(0x20 + i % (0x7f - 0x20) for i in bytearray(os.urandom(l))))

if __name__ == '__main__':
    cipher = RSA(bits=32,seed = 0xfffff)
    
    print('Key:')
    cipher.key.dump()
    s = "31569065655.546946{'proof-of-work': 3289094117, 'transactions': [{'from': 'network', 'to': 'q3nf394hjg-random-miner-address-34nf3i4nflkn3oi', 'amount': 1}]}32RSAKey(N=0x21bae4af1, e=0x10001)"
    
    c = cipher.encrypt_data(s)
    print('Encrypted:  %s' % c)
    m = cipher.decrypt_data(c)
    print('Decrypted:  %s' % m)
