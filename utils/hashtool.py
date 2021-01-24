import hashlib


def hash2mark(timestamp, nonce):
    nonce = str(nonce)
    length = len(nonce)
    timestamp = str(timestamp)
    mixed = nonce[:length//2] + timestamp + nonce[length//2:]
    return hashlib.md5(mixed.encode('utf-8')).hexdigest()
