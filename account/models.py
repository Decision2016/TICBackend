from django.db import models
from django.contrib.auth.models import AbstractUser


class AdminUser(AbstractUser):
    username = models.CharField(max_length=256, unique=True)
    email = models.EmailField()
    google_secret = models.CharField(max_length=16, null=True)
    errCount = models.IntegerField(default=0)
    errTimestamp = models.BigIntegerField(null=True)

    class Meta:
        db_table = "tic_admin_list"


class Cache(models.Model):
    mark_info = models.CharField(max_length=128, primary_key=True)
    public = models.TextField()
    secret = models.TextField()
    timestamp = models.BigIntegerField()
    ip_address = models.CharField(max_length=64)

    class Meta:
        db_table = "tic_cache"


class Carousel(models.Model):
    _id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=256)
    description = models.TextField()

    class Meta:
        db_table = "tic_carousel"


class Personnel(models.Model):
    _id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    avatar = models.CharField(max_length=128)
    duties = models.CharField(max_length=30)

    class Meta:
        db_table = "tic_personnel"


class ImgSource(models.Model):
    _id = models.AutoField(primary_key=True)
    path = models.TextField(max_length=128)
    md5 = models.TextField(max_length=128)

    class Meta:
        db_table = "tic_resource"


class WebsiteInfo(models.Model):
    _id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    record = models.CharField(max_length=256)
    record_switch = models.BooleanField(default=False)
    maintain = models.BooleanField(default=False)