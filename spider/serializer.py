from rest_framework import serializers
from .models import VXPage


class VXPageHomeSerializer(serializers.Serializer):
    _id = serializers.IntegerField()
    title = serializers.CharField()
    author = serializers.CharField()
    date = serializers.DateField()
    description = serializers.CharField()

    class Meta:
        model = VXPage


class VXPageSerializer(serializers.Serializer):
    context = serializers.CharField()

    class Meta:
        model = VXPage
