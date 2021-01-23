from rest_framework.response import Response
import functools


class BaseDecorator(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, obj_type):
        return functools.partial(self.__call__, obj)

    @staticmethod
    def error(msg):
        return Response({"errMsg": -1, "data": msg})

    def __call__(self, *args, **kwargs):
        self.request = args[1]

        if self.check_permission():
            return self.func(*args, **kwargs)
        else:
            return self.error("Please login first.")

    def check_permission(self):
        raise NotImplementedError()


class login_required(BaseDecorator):
    def check_permission(self):
        user = self.request.user
        return user.is_authenticated

