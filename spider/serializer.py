from rest_framework import serializers
from .models import VXPage


class VXPageHomeSerializer(serializers.Serializer):
    title = serializers.CharField()
    author = serializers.CharField()
    datetime = serializers.DateTimeField()
    description = serializers.CharField()

    class Meta:
        model = VXPage


class VXPageSerializer(serializers.Serializer):
    context = serializers.CharField()

    class Meta:
        model = VXPage
