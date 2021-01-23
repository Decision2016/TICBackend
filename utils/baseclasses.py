from rest_framework.views import APIView
from rest_framework.response import Response


class BaseAPIView(APIView):
    @staticmethod
    def error(msg):
        res = {'code': -1, 'data': msg}
        return Response(res)

    @staticmethod
    def success(msg):
        res = {'code': 0, 'data': msg}
        return Response(res)

    @staticmethod
    def info(msg):
        res = {'code': -10, 'data': msg}
        return Response(res)