import time
import os


def timestamp():
    return int(time.time())


def get_env(name, default=""):
    return os.environ.get(name, default)


def user_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    return ip
