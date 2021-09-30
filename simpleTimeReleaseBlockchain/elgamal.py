import random
# import math
import sys


class PrivateKey(object):
    def __init__(self, p=None, g=None, x=None, i_num_bits=0):
        self.p = p
        self.g = g
        self.x = x
        self.difficulty = i_num_bits


class PublicKey(object):
    def __init__(self, p=None, g=None, h=None, i_num_bits=0):
        self.p = p
        self.g = g
        self.h = h
        self.difficulty = i_num_bits
        self.x = None


# computes the greatest common denominator of a and b.  assumes a > b
def gcd(a, b):
    while b != 0:
        c = a % b
        a = b
        b = c
    # a is returned if b == 0
    return a


# computes base^exp mod modulus
def mod_exp(base, exp, modulus):
    return pow(base, exp, modulus)


# solovay-strassen primality test.  tests if num is prime
def solovay_strassen(num, i_confidence):
    # ensure confidence of t
    for idx in range(i_confidence):
        # choose random a between 1 and n-2
        a = random.randint(1, num - 1)

        # if a is not relatively prime to n, n is composite
        if gcd(a, num) > 1:
            return False

        # declares n prime if jacobi(a, n) is congruent to a^((n-1)/2) mod n
        if not jacobi(a, num) % num == mod_exp(a, (num - 1) // 2, num):
            return False

    # if there have been t iterations without failure, num is believed to be prime
    return True


# computes the jacobi symbol of a, n
def jacobi(a, n):
    if a == 0:
        if n == 1:
            return 1
        else:
            return 0
    # property 1 of the jacobi symbol
    elif a == -1:
        if n % 2 == 0:
            return 1
        else:
            return -1
    # if a == 1, jacobi symbol is equal to 1
    elif a == 1:
        return 1
    # property 4 of the jacobi symbol
    elif a == 2:
        if n % 8 == 1 or n % 8 == 7:
            return 1
        elif n % 8 == 3 or n % 8 == 5:
            return -1
    # property of the jacobi symbol:
    # if a = b mod n, jacobi(a, n) = jacobi( b, n )
    elif a >= n:
        return jacobi(a % n, n)
    elif a % 2 == 0:
        return jacobi(2, n) * jacobi(a // 2, n)
    # law of quadratic reciprocity
    # if a is odd and a is co-prime to n
    else:
        if a % 4 == 3 and n % 4 == 3:
            return -1 * jacobi(n, a)
        else:
            return jacobi(n, a)


# finds a primitive root for prime p
# this function was implemented from the algorithm described here:
# http://modular.math.washington.edu/edu/2007/spring/ent/ent-html/node31.html
def find_primitive_root(p, seed):
    random.seed(seed)
    if p == 2:
        return 1
    # the prime divisors of p-1 are 2 and (p-1)/2 because
    # p = 2x + 1 where x is a prime
    p1 = 2
    p2 = (p - 1) // p1

    # test random g's until one is found that is a primitive root mod p
    while True:
        g = random.randint(2, p - 1)
        # g is a primitive root if for all prime factors of p-1, p[i]
        # g^((p-1)/p[i]) (mod p) is not congruent to 1
        if not (mod_exp(g, (p - 1) // p1, p) == 1):
            if not mod_exp(g, (p - 1) // p2, p) == 1:
                return g


# find n bit prime
def find_prime(i_num_bits, i_confidence, seed):
    random.seed(seed)
    # keep testing until one is found
    while True:
        # generate potential prime randomly
        p = random.randint(2 ** (i_num_bits - 2), 2 ** (i_num_bits - 1))
        # make sure it is odd
        while p % 2 == 0:
            p = random.randint(2 ** (i_num_bits - 2), 2 ** (i_num_bits - 1))

        # keep doing this if the solovay-strassen test fails
        while not solovay_strassen(p, i_confidence):
            p = random.randint(2 ** (i_num_bits - 2), 2 ** (i_num_bits - 1))
            while p % 2 == 0:
                p = random.randint(2 ** (i_num_bits - 2), 2 ** (i_num_bits - 1))

        # if p is prime compute p = 2*p + 1
        # if p is prime, we have succeeded; else, start over
        p = p * 2 + 1
        if solovay_strassen(p, i_confidence):
            return p


# encodes bytes to integers mod p.  reads bytes from file
def encode(s_plaintext, i_num_bits):
    byte_array = bytearray(s_plaintext, 'utf-16')

    # z is the array of integers mod p
    z = []

    # each encoded integer will be a linear combination of k message bytes
    # k must be the number of bits in the prime divided by 8 because each
    # message byte is 8 bits long
    k = i_num_bits // 8

    # j marks the jth encoded integer
    # j will start at 0 but make it -k because j will be incremented during first iteration
    j = -1 * k
    # num is the summation of the message bytes
    # num = 0
    # i iterates through byte array
    for idx in range(len(byte_array)):
        # if i is divisible by k, start a new encoded integer
        if idx % k == 0:
            j += k
            # num = 0
            z.append(0)
        # add the byte multiplied by 2 raised to a multiple of 8
        z[j // k] += byte_array[idx] * (2 ** (8 * (idx % k)))

    # example
    # if n = 24, k = n / 8 = 3
    # z[0] = (summation from i = 0 to i = k)m[i]*(2^(8*i))
    # where m[i] is the ith message byte

    # return array of encoded integers
    return z


# decodes integers to the original message bytes
def decode(plaintext_list, i_num_bits):
    # bytes array will hold the decoded original message bytes
    bytes_array = []

    # same deal as in the encode function.
    # each encoded integer is a linear combination of k message bytes
    # k must be the number of bits in the prime divided by 8 because each
    # message byte is 8 bits long
    k = i_num_bits // 8

    # num is an integer in list aiPlaintext
    for num in plaintext_list:
        # get the k message bytes from the integer, i counts from 0 to k-1
        for idx in range(k):
            # temporary integer
            temp = num
            # j goes from i+1 to k-1
            for j in range(idx + 1, k):
                # get remainder from dividing integer by 2^(8*j)
                temp = temp % (2 ** (8 * j))
            # message byte representing a letter is equal to temp divided by 2^(8*i)
            letter = temp // (2 ** (8 * idx))
            # add the message byte letter to the byte array
            bytes_array.append(letter)
            # subtract the letter multiplied by the power of two from num so
            # so the next message byte can be found
            num = num - (letter * (2 ** (8 * idx)))

    # example
    # if "You" were encoded.
    # Letter        #ASCII
    # Y              89
    # o              111
    # u              117
    # if the encoded integer is 7696217 and k = 3
    # m[0] = 7696217 % 256 % 65536 / (2^(8*0)) = 89 = 'Y'
    # 7696217 - (89 * (2^(8*0))) = 7696128
    # m[1] = 7696128 % 65536 / (2^(8*1)) = 111 = 'o'
    # 7696128 - (111 * (2^(8*1))) = 7667712
    # m[2] = 7667712 / (2^(8*2)) = 117 = 'u'

    decoded_text = bytearray(b for b in bytes_array).decode('utf-16')

    return decoded_text


# generates public key K1 (p, g, h) and private key K2 (p, g, x)
def generate_keys(seed, i_num_bits, i_confidence=32):
    # p is the prime
    # g is the primitive root
    # x is random in (0, p-1) inclusive
    # h = g ^ x mod p

    p = find_prime(i_num_bits, i_confidence, seed)
    g = find_primitive_root(p, seed)
    # h = mod_exp(g, 2, p)
    # x = random.randint( 1, p - 1)
    # h = mod_exp(g,x,p)

    h = random.randint(1, p - 1)

    public_key = PublicKey(p, g, h, i_num_bits)
    # privateKey = PrivateKey(p, g, x, iNumBits)

    return public_key


# encrypts a string using the public key k
def encrypt(key, s_plaintext):
    z = encode(s_plaintext, key.difficulty)

    # cipher_pairs list will hold pairs (c, d) corresponding to each integer in z
    cipher_pairs = []
    # i is an integer in z
    for i_code in z:
        # pick random y from (0, p-1) inclusive
        y = random.randint(0, key.p)
        # c = g^y mod p
        c = mod_exp(key.g, y, key.p)
        # d = ih^y mod p
        d = (i_code * mod_exp(key.h, y, key.p)) % key.p
        # add the pair to the cipher pairs list
        cipher_pairs.append([c, d])

    encrypted_str = ""
    for pair in cipher_pairs:
        encrypted_str += str(pair[0]) + ' ' + str(pair[1]) + ' '

    return encrypted_str


# performs decryption on the cipher pairs found in Cipher using
# private key K2 and writes the decrypted values to file Plaintext
def decrypt(key, cipher_string):
    # decrypts each pair and adds the decrypted integer to list of plaintext integers
    plaintext = []

    cipher_array = cipher_string.split()
    if not len(cipher_array) % 2 == 0:
        return "Malformed Cipher Text"
    for idx in range(0, len(cipher_array), 2):
        # c = first number in pair
        c = int(cipher_array[idx])
        # d = second number in pair
        d = int(cipher_array[idx + 1])

        # s = c^x mod p
        s = mod_exp(c, key.x, key.p)
        # plaintext integer = ds^-1 mod p
        plain_i = (d * mod_exp(s, key.p - 2, key.p)) % key.p
        # add plain to list of plaintext integers
        plaintext.append(plain_i)

    decrypted_text = decode(plaintext, key.difficulty)

    # remove trailing null bytes
    decrypted_text = "".join([ch for ch in decrypted_text if ch != '\x00'])

    return decrypted_text

