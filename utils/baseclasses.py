from rest_framework.views import APIView
from rest_framework.response import Response


class BaseAPIView(APIView):
    @staticmethod
    def error(msg=None):
        res = {'code': -1, 'data': msg}
        return Response(res)

    @staticmethod
    def success(msg=None):
        res = {'code': 0, 'data': msg}
        return Response(res)

    @staticmethod
    def info(msg=None):
        res = {'code': -10, 'data': msg}
        return Response(res)

    @staticmethod
    def params_error(msg=None):
        res = {'code': 1, 'data': msg}
        return Response(res)

    @staticmethod
    def frequent():
        res = {'code': 5, 'data': {
            'errMsg': 'Parameter error.'
        }}
        return Response(res)