import hashlib
import time
import base64
import hmac
import struct
from .contants import google_sec

secretString = google_sec


def generate_secret():
    timestamp = int(time.time())
    half = len(secretString) // 2
    import_str = secretString[:half] + str(timestamp) + secretString[half:]
    digest = hashlib.sha256(import_str.encode('utf-8')).hexdigest()
    base32code = base64.b32encode(bytes.fromhex(digest))
    sec_code = bytes.decode(base32code[:16])
    return sec_code


def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(normalize(secret), True)  # True is to fold lower into uppercase
    msg = struct.pack(">Q", intervals_no)
    h = bytearray(hmac.new(key, msg, hashlib.sha1).digest())
    o = h[19] & 15
    h = str((struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000)
    return prefix0(h)


def generate_pin(secret_code):
    return (get_hotp_token(secret_code, intervals_no=int(time.time()) // 30 - 1),
            get_hotp_token(secret_code, intervals_no=int(time.time()) // 30),
            get_hotp_token(secret_code, intervals_no=int(time.time()) // 30 + 1))


def normalize(key):
    k2 = key.strip().replace(' ', '')
    if len(k2) % 8 != 0:
        k2 += '=' * (8 - len(k2) % 8)
    return k2


def prefix0(h):
    if len(h) < 6:
        h = '0' * (6 - len(h)) + h
    return h


