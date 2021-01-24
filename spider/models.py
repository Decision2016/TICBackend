from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class VXPage(models.Model):
    _id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=30)
    avatar = models.CharField(max_length=128)
    datetime = models.DateTimeField(auto_now=True)
    description = models.TextField()
    context = models.TextField()

    class Meta:
        db_table = "tic_vxpage"