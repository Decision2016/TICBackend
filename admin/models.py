from django.db import models
from django.contrib.auth.models import AbstractUser


class AdminUser(AbstractUser):
    username = models.TextField(unique=True)

    class Meta:
        db_table = "tic_admin_list"


class VXPage(models.Model):
    _id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=30)
    avatar = models.CharField(max_length=128)
    context = models.CharField()

    class Meta:
        db_table = "tic_vxpage"


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
